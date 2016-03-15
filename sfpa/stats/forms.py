import django.forms
from .models import Player, Team, Game

WINNER_CHOICES = (
    ('home', 'Home'),
    ('away', 'Away'),
)


class PlayerForm(django.forms.ModelForm):
    class Meta:
        model = Player
        exclude = []
    team = django.forms.ModelChoiceField(queryset=Team.objects.filter(season__is_default__exact=True))


class ScoreSheetGameForm(django.forms.ModelForm):
    class Meta:
        model = Game
        # exclude = ['order', 'home_player', 'away_player']
        fields = ['winner', 'table_run', 'forfeit']
        extra = 0
        # TODO: de-hard-code this
        # max_num = 16
        widgets = {
            'winner': django.forms.RadioSelect(
                choices=WINNER_CHOICES
            )
        }
        labels = {
            'winner': '',
            'table_run': '',
            'forfeit': '',
        }
