from flask import Blueprint

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/tomek')
def wodzionka():
    text = "<p>Mmmm. Wodzionka, suchy chlyb i wody szklonka.<br>Mmmm. Wodzionka, to nojlepszo z wszystkich ślonskich zup.<br> Mmmm. Wodzionka, jak jom zrobi moja żonka.<br> Mmmm. Wodzionka, to jes łósmy świata cud.</p>"
    return text

@misc_bp.route('/olek/<tekst>')
def papuga(tekst):
    tekst = "<p>🦜" + tekst + "</p>"
    return tekst

@misc_bp.route('/Filip_Fujak')
def grruszki_w_winie():
    return '<p>Potem wrzucę przepis jak się rozbudzę ^^</p>'