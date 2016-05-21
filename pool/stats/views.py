import time

from django.shortcuts import render, redirect
from .models import Division, AwayLineupEntry, Game, HomeLineupEntry, Match, Player, \
    ScoreSheet, Season, Sponsor, Team, Week
from .models import PlayPosition
from .models import PlayerSeasonSummary
from .models import AwaySubstitution, HomeSubstitution
from .forms import PlayerForm, ScoreSheetGameForm, DisabledScoreSheetGameForm, ScoreSheetCompletionForm
from django.forms import modelformset_factory

import django.forms
import django.db.models

import logging
logger = logging.getLogger(__name__)


def session_uid(request):
    if 'uid' not in request.session.keys():
        request.session['uid'] = str(hash(time.time()))[0:15]
    return request.session['uid']


def set_season(request, season_id=None):
    """
    Allow the user to set their season to a value other than the default.
    :param request:
    :param season_id: the season to use, if not the current default
    :return: bool
    """
    if season_id is None:
        season_id = Season.objects.get(is_default=True).id
    request.session['season_id'] = season_id
    request.session.save()
    # hard-coded urls are bad okay?
    return redirect(request.META.get('HTTP_REFERER', '/stats/'))


def check_season(request):
    if 'season_id' in request.session:
        return
    else:
        set_season(request)


def index(request):
    print(__name__)
    logger.error("this is {}".format(__name__))
    check_season(request)
    team_list = Team.objects.filter(season=request.session['season_id']).order_by('-win_percentage')
    season = Season.objects.get(id=request.session['season_id'])
    context = {
        'teams': team_list,
        'season': season,
    }
    return render(request, 'stats/teams.html', context)


def player(request, player_id):
    check_season(request)
    _player = Player.objects.get(id=player_id)
    summaries = PlayerSeasonSummary.objects.filter(player__exact=_player).order_by('-season')

    _score_sheets = ScoreSheet.objects.filter(official=True)

    # the set() is necessary to remove the dupes apparently created by the or clause
    _score_sheets = set(_score_sheets.filter(
        django.db.models.Q(away_lineup__player=_player) | django.db.models.Q(home_lineup__player=_player)
    ))

    context = {
        'score_sheets': _score_sheets,
        'summaries': summaries,
        'player': _player
    }
    return render(request, 'stats/player.html', context)


def players(request):
    check_season(request)
    _players = PlayerSeasonSummary.objects.filter(
        season=request.session['season_id'],
        ranking__gt=0
    ).order_by('-win_percentage', '-wins')

    context = {
        'players': _players
    }
    return render(request, 'stats/players.html', context)


def player_create(request):
    if request.method == 'POST':
        player_form = PlayerForm(request.POST)
        if player_form.is_valid():
            p = Player()
            logger.debug(player_form.cleaned_data['team'])
            t = player_form.cleaned_data['team']
            if player_form.cleaned_data['display_name'] is not '':
                p.display_name = player_form.cleaned_data['display_name']
            p.first_name = player_form.cleaned_data['first_name']
            p.last_name = player_form.cleaned_data['last_name']
            p.save()
            t.players.add(p)
            return redirect('team', t.id)
    else:
        player_form = PlayerForm()
    context = {
        'form': player_form
    }
    return render(request, 'stats/player_create.html', context)


def update_players_stats(request):

    PlayerSeasonSummary.update_all(season_id=request.session['season_id'])

    return redirect('/stats/players')


def team(request, team_id):

    _team = Team.objects.get(id=team_id)
    _players = PlayerSeasonSummary.objects.filter(player_id__in=list([x.id for x in _team.players.all()]))
    _score_sheets = set(ScoreSheet.objects.filter(official=True).filter(
        django.db.models.Q(match__away_team=_team) | django.db.models.Q(match__home_team=_team)
    ))

    context = {
        'team': _team,
        'players': _players,
        'scoresheets': _score_sheets
    }
    return render(request, 'stats/team.html', context)


def seasons(request):
    _seasons = Season.objects.all()
    context = {
        'seasons': _seasons
    }
    return render(request, 'stats/seasons.html', context)


def sponsor(request, sponsor_id):
    _sponsor = Sponsor.objects.get(id=sponsor_id)
    context = {
        'sponsor': _sponsor
    }
    return render(request, 'stats/sponsor.html', context)


def sponsors(request):
    _sponsors = Sponsor.objects.all()
    context = {
        'sponsors': _sponsors
    }
    return render(request, 'stats/sponsors.html', context)


def divisions(request):
    check_season(request)
    _divisions = Division.objects.filter(season=request.session['season_id']).order_by('id')
    # this wrapper divisions dodge is needed so the teams within each division
    # can be sorted by ranking
    wrapper_divisions = []
    for _division in _divisions:
        teams = Team.objects.filter(division=_division).order_by('ranking')
        wrapper_divisions.append({
            'division': _division,
            'teams': teams
        })
    context = {
        'divisions': _divisions,
        'wrapper_divisions': wrapper_divisions

    }
    return render(request, 'stats/divisions.html', context)


def week(request, week_id):
    _week = Week.objects.get(id=week_id)

    official_matches = []
    unofficial_matches = []

    for a_match in _week.match_set.all():
        # an 'official' match has exactly one score sheet, which has been marked official;
        # also in the template, official matches are represented by their score sheet,
        # unofficial matches by the match
        match_score_sheets = ScoreSheet.objects.filter(match=a_match)
        if len(match_score_sheets.filter(official=True)) == 1:
            official_matches.append(match_score_sheets.filter(official=True)[0])
        else:
            unofficial_matches.append(a_match)

    context = {
        'week': _week,
        'unofficial_matches': unofficial_matches,
        'official_matches': official_matches
    }
    return render(request, 'stats/week.html', context)


def weeks(request):
    check_season(request)
    _season = Season.objects.get(id=request.session['season_id'])
    _weeks = Week.objects.filter(season=request.session['season_id'])
    context = {
        'weeks': _weeks,
        'season': _season
    }
    return render(request, 'stats/weeks.html', context)


def match(request, match_id):
    _match = Match.objects.get(id=match_id)
    match_score_sheets = ScoreSheet.objects.filter(match_id__exact=_match.id, official=True)

    score_sheet_game_formsets = None

    if len(match_score_sheets):
        score_sheet_game_formset_f = modelformset_factory(
            model=Game,
            form=DisabledScoreSheetGameForm,
            max_num=len(match_score_sheets[0].games.all())
        )
        score_sheet_game_formsets = []
        for a_score_sheet in match_score_sheets:
            score_sheet_game_formsets.append(
                score_sheet_game_formset_f(
                    queryset=a_score_sheet.games.all(),
                )
            )
    context = {
        'match': _match,
        'score_sheets': score_sheet_game_formsets
    }
    return render(request, 'stats/match.html', context)


def score_sheets(request):
    sheets = ScoreSheet.objects.filter(official=False)

    sheets_with_scores = []
    for sheet in sheets:
        sheets_with_scores.append({
            'sheet': sheet,
        })

    context = {
        'score_sheets': sheets_with_scores
    }
    return render(request, 'stats/score_sheets.html', context)


def score_sheet(request, score_sheet_id):
    s = ScoreSheet.objects.get(id=score_sheet_id)
    score_sheet_game_formset_f = modelformset_factory(
        Game,
        form=DisabledScoreSheetGameForm,
        max_num=len(s.games.all()),
    )
    score_sheet_game_formset = score_sheet_game_formset_f(
        queryset=s.games.all(),
    )

    context = {
        'score_sheet': s,
        'games_formset': score_sheet_game_formset,
        'away_player_score_sheet_summaries': s.player_summaries('away'),
        'home_player_score_sheet_summaries': s.player_summaries('home')
    }
    return render(request, 'stats/score_sheet.html', context)


def score_sheet_complete(request, score_sheet_id):
    s = ScoreSheet.objects.get(id=score_sheet_id)
    score_sheet_game_formset_f = modelformset_factory(
        Game,
        form=DisabledScoreSheetGameForm,
        max_num=len(s.games.all()),
    )
    score_sheet_game_formset = score_sheet_game_formset_f(
        queryset=s.games.all(),
    )

    if request.method == 'POST':
        score_sheet_completion_form = ScoreSheetCompletionForm(request.POST, instance=s)
        if score_sheet_completion_form.is_valid():
            score_sheet_completion_form.save()
            return redirect('week', s.match.week.id)
    else:
        score_sheet_completion_form = ScoreSheetCompletionForm(
            instance=s,
        )

    context = {
        'score_sheet': s,
        'games_formset': score_sheet_game_formset,
        'away_player_score_sheet_summaries': s.player_summaries('away'),
        'home_player_score_sheet_summaries': s.player_summaries('home'),
        'score_sheet_completion_form': score_sheet_completion_form,
    }
    return render(request, 'stats/score_sheet_complete.html', context)


def score_sheet_edit(request, score_sheet_id):
    s = ScoreSheet.objects.get(id=score_sheet_id)
    if session_uid(request) != s.creator_session:
        if not request.user.is_superuser:
            return redirect('score_sheet', s.id)
    score_sheet_game_formset_f = modelformset_factory(
        Game,
        form=ScoreSheetGameForm,
        max_num=len(s.games.all())
    )
    if request.method == 'POST':
        score_sheet_game_formset = score_sheet_game_formset_f(
            request.POST, queryset=s.games.all()
        )
        if score_sheet_game_formset.is_valid():
            score_sheet_game_formset.save()
    else:
        score_sheet_game_formset = score_sheet_game_formset_f(
            queryset=s.games.all(),
        )
    context = {
        'score_sheet': s,
        'games_formset': score_sheet_game_formset,
    }
    return render(request, 'stats/score_sheet_edit.html', context)


def score_sheet_create(request, match_id):
    # m = Match.objects.get(id=match_id)
    s = ScoreSheet(match=Match.objects.get(id=match_id))
    s.creator_session = session_uid(request)
    s.save()
    s.initialize_lineup()
    s.initialize_games()

    return redirect('score_sheet_edit', score_sheet_id=s.id)


def score_sheet_lineup(request, score_sheet_id, away_home):
    s = ScoreSheet.objects.get(id=score_sheet_id)

    # it would be prettier to do this by passing kwargs but,
    # it seems you can't do that with a ModelForm so, the ugly is here.
    lineup_players_queryset = s.match.away_team.players.all()
    lineup_queryset = s.away_lineup.all()
    lineup_model = AwayLineupEntry
    if away_home == 'home':
        lineup_players_queryset = s.match.home_team.players.all()
        lineup_queryset = s.home_lineup.all()
        lineup_model = HomeLineupEntry

    class LineupForm(django.forms.ModelForm):
        # thanks to stack overflow for this, from here:
        # http://stackoverflow.com/questions/1982025/django-form-from-related-model
        player = django.forms.ModelChoiceField(
            queryset=lineup_players_queryset,
            required=False,
        )

    lineup_formset_f = modelformset_factory(
        model=lineup_model, fields=['player'], form=LineupForm,
        extra=0, max_num=len(PlayPosition.objects.all())
    )

    if request.method == 'POST':
        lineup_formset = lineup_formset_f(request.POST, queryset=lineup_queryset)
        if lineup_formset.is_valid():
            lineup_formset.save()
            s.set_games()
            return redirect('score_sheet_edit', score_sheet_id=s.id)
    else:
        lineup_formset = lineup_formset_f(queryset=lineup_queryset)

    context = {
        'score_sheet': s,
        'lineup_formset': lineup_formset,
        'away_home': away_home
    }
    return render(request, 'stats/score_sheet_lineup_edit.html', context)


def score_sheet_substitutions(request, score_sheet_id, away_home):
    s = ScoreSheet.objects.get(id=score_sheet_id)

    substitution_players_queryset = s.match.away_team.players.all()
    substitution_queryset = s.away_substitutions.all()
    substitution_model = AwaySubstitution
    add_substitution_function = s.away_substitutions.add
    if away_home == 'home':
        substitution_players_queryset = s.match.home_team.players.all()
        substitution_queryset = s.home_substitutions.all()
        substitution_model = HomeSubstitution
        add_substitution_function = s.home_substitutions.add

    class SubstitutionForm(django.forms.ModelForm):
        player = django.forms.ModelChoiceField(
            queryset=substitution_players_queryset,
            required=False,
        )

    substitution_formset_f = modelformset_factory(
        model=substitution_model,
        form=SubstitutionForm,
        fields=['game_order', 'player', 'play_position'],
        max_num=2
    )
    if request.method == 'POST':
        substitution_formset = substitution_formset_f(
            request.POST, queryset=substitution_queryset
        )
        if substitution_formset.is_valid():
            logging.debug('saving {} subs for {}'.format(away_home, s.match))
            for substitution in substitution_formset.save():
                logging.debug('adding {} as {} in game {}'.format(
                    substitution.player, substitution.play_position, substitution.game_order))
                add_substitution_function(substitution)
            s.set_games()
            return redirect('score_sheet_edit', score_sheet_id=s.id)
    else:
        substitution_formset = substitution_formset_f(queryset=substitution_queryset)
        context = {
            'score_sheet': s,
            'substitutions_form': substitution_formset,
            'away_home': away_home,
        }
        return render(request, 'stats/score_sheet_substitutions.html', context)


def update_teams_stats(request):
    # be sure about what season we are working on
    check_season(request)
    Team.update_teams_stats(season_id=request.session['season_id'])
    return redirect('teams')


def unofficial_results(request):
    sheets = ScoreSheet.objects.filter(official=False)

    context = {
        'score_sheets': sheets,
    }

    return render(request, 'stats/unofficial_results.html', context)
