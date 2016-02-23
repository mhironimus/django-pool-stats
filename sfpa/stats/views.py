from django.shortcuts import render, redirect
from .models import Division, Player, Season, Sponsor, Team, Week


def set_season(request, season_id=None):
    """
    Allow the user to set their season to a value other than the default.
    :param request:
    :return: bool
    """
    if season_id is None:
        season_id = Season.objects.get(is_default=True).id
    request.session['season_id'] = season_id
    request.session.save()
    # hard-coded urls are bad okay?
    return redirect(to='/stats/')


def check_season(request):
    if 'season_id' in request.session:
        return
    else:
        set_season(request)


def index(request):
    check_season(request)
    team_list = Team.objects.filter(season=request.session['season_id'])
    season = Season.objects.get(id=request.session['season_id'])
    context = {
        'teams': team_list,
        'season': season,
    }
    return render(request, 'stats/teams.html', context)


def player(request, player_id):
    _player = Player.objects.get(id=player_id)
    context = {
        'player': _player
    }
    return render(request, 'stats/player.html', context)


def players(request):
    #  filter on membership in a team in the current season
    check_season(request)
    _players = Player.objects.filter(team__season=request.session['season_id'])
    context = {
        'players': _players
    }
    return render(request, 'stats/players.html', context)


def team(request, team_id):

    _team = Team.objects.get(id=team_id)
    context = {
        'team': _team
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
    _divisions = Division.objects.filter(season=request.session['season_id'])
    context = {
        'divisions': _divisions
    }
    return render(request, 'stats/divisions.html', context)


def week(request, week_id):
    check_season(request)
    _week = Week.objects.get(id=week_id)
    context = {
        'week': _week
    }
    return render(request, 'stats/week.html', context)


def weeks(request):
    check_season(request)
    _weeks = Week.objects.filter(season=request.session['season_id'])
    context = {
        'weeks': _weeks
    }
    return render(request, 'stats/weeks.html', context)
