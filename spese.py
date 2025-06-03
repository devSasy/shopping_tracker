import io
import csv
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from decimal import Decimal, InvalidOperation
from datetime import datetime
from models import Spesa
from auth import login_required

spese_bp = Blueprint('spese', __name__)

@spese_bp.route('/')
@login_required
def index():
    """Pagina principale con elenco delle spese dell'utente loggato"""
    user_id = session.get('user_id')
    spese = Spesa.get_all(user_id=user_id)
    totale = sum(spesa.importo for spesa in spese if spesa.importo)
    categorie = Spesa.get_categorie(user_id=user_id)
    
    return render_template('index.html', spese=spese, totale=totale, categorie=categorie)

@spese_bp.route('/add', methods=['POST'])
@login_required
def add_spesa():
    """Aggiunge una nuova spesa dopo validazione dei dati"""
    user_id = session.get('user_id')
    
    data = request.form.get('data')
    categoria = request.form.get('categoria')
    descrizione = request.form.get('descrizione')
    importo = request.form.get('importo')
    
    errors = []
    
    if not data:
        errors.append("La data è obbligatoria")
    else:
        try:
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            errors.append("Formato data non valido (YYYY-MM-DD)")
    
    if not categoria:
        errors.append("La categoria è obbligatoria")
    
    if not descrizione:
        errors.append("La descrizione è obbligatoria")
    
    if not importo:
        errors.append("L'importo è obbligatorio")
    else:
        try:
            importo_decimal = Decimal(importo.replace(',', '.'))
            if importo_decimal <= 0:
                errors.append("L'importo deve essere maggiore di zero")
        except InvalidOperation:
            errors.append("Importo non valido")
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('spese.index'))
    
    spesa = Spesa(
        user_id=user_id,
        data=data,
        categoria=categoria,
        descrizione=descrizione,
        importo=importo_decimal
    )
    
    if spesa.save():
        flash('Spesa aggiunta con successo!', 'success')
    else:
        flash('Errore durante il salvataggio della spesa', 'danger')
    
    return redirect(url_for('spese.index'))

@spese_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_spesa(id):
    """Modifica una spesa esistente"""
    user_id = session.get('user_id')
    spesa = Spesa.get_by_id(id, user_id)
    
    if not spesa:
        flash('Spesa non trovata o non autorizzata', 'danger')
        return redirect(url_for('spese.index'))
    
    if request.method == 'POST':
        data = request.form.get('data')
        categoria = request.form.get('categoria')
        descrizione = request.form.get('descrizione')
        importo = request.form.get('importo')
        
        errors = []
        
        if not data:
            errors.append("La data è obbligatoria")
        else:
            try:
                datetime.strptime(data, "%Y-%m-%d")
            except ValueError:
                errors.append("Formato data non valido (YYYY-MM-DD)")
        
        if not categoria:
            errors.append("La categoria è obbligatoria")
        
        if not descrizione:
            errors.append("La descrizione è obbligatoria")
        
        if not importo:
            errors.append("L'importo è obbligatorio")
        else:
            try:
                importo_decimal = Decimal(importo.replace(',', '.'))
                if importo_decimal <= 0:
                    errors.append("L'importo deve essere maggiore di zero")
            except InvalidOperation:
                errors.append("Importo non valido")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('spese.edit_spesa', id=id))
        
        spesa.data = datetime.strptime(data, "%Y-%m-%d").date()
        spesa.categoria = categoria
        spesa.descrizione = descrizione
        spesa.importo = importo_decimal
        
        if spesa.save():
            flash('Spesa aggiornata con successo!', 'success')
            return redirect(url_for('spese.index'))
        else:
            flash('Errore durante l\'aggiornamento della spesa', 'danger')
    
    categorie = Spesa.get_categorie(user_id=user_id)
    return render_template('edit.html', spesa=spesa, categorie=categorie)

@spese_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_spesa(id):
    """Elimina una spesa"""
    user_id = session.get('user_id')
    spesa = Spesa.get_by_id(id, user_id)
    
    if not spesa:
        flash('Spesa non trovata o non autorizzata', 'danger')
    elif spesa.delete():
        flash('Spesa eliminata con successo!', 'success')
    else:
        flash('Errore durante l\'eliminazione della spesa', 'danger')
    
    return redirect(url_for('spese.index'))

@spese_bp.route('/filter')
@login_required
def filter_spese():
    """Filtra le spese per categoria e/o mese (query string)"""
    user_id = session.get('user_id')
    categoria = request.args.get('categoria')
    mese = request.args.get('mese')
    
    filters = {}
    if categoria:
        filters['categoria'] = categoria
    if mese:
        filters['mese'] = mese
    
    spese = Spesa.get_all(user_id=user_id, filters=filters)
    totale = sum(spesa.importo for spesa in spese if spesa.importo)
    
    categorie = Spesa.get_categorie(user_id=user_id)
    mesi = Spesa.get_mesi(user_id=user_id)
    
    return render_template(
        'report.html', 
        spese=spese, 
        totale=totale, 
        categorie=categorie, 
        mesi=mesi,
        selected_categoria=categoria,
        selected_mese=mese
    )

@spese_bp.route('/export')
@login_required
def export_spese():
    """Esporta le spese filtrate in un file CSV che poi sarà scaricabile"""
    user_id = session.get('user_id')
    categoria = request.args.get('categoria')
    mese = request.args.get('mese')
    
    filters = {}
    if categoria:
        filters['categoria'] = categoria
    if mese:
        filters['mese'] = mese
    
    spese = Spesa.get_all(user_id=user_id, filters=filters)
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'user_id', 'data', 'categoria', 'descrizione', 'importo'])
    writer.writeheader()
    
    for spesa in spese:
        writer.writerow(spesa.to_dict())
    
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    output.close()
    
    filename = "spese"
    if categoria:
        filename += f"_{categoria}"
    if mese:
        filename += f"_{mese}"
    filename += ".csv"
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )