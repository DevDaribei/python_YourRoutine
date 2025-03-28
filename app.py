from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    language = db.Column(db.String(2), default='pt')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activities = db.relationship('Activity', backref='user', lazy=True)
    assessments = db.relationship('Assessment', backref='user', lazy=True)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    time = db.Column(db.Integer, nullable=False)
    satisfaction = db.Column(db.Integer, nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)

# Category colors and icons
CATEGORY_COLORS = {
    'leisure': {'bg': '#FFF3E0', 'border': '#FF9800', 'icon': '🎮'},
    'career': {'bg': '#E3F2FD', 'border': '#2196F3', 'icon': '💼'},
    'health': {'bg': '#E8F5E9', 'border': '#4CAF50', 'icon': '💪'},
    'relationships': {'bg': '#FCE4EC', 'border': '#E91E63', 'icon': '❤️'},
    'personal_development': {'bg': '#F3E5F5', 'border': '#9C27B0', 'icon': '🎯'},
    'finances': {'bg': '#E0F2F1', 'border': '#009688', 'icon': '💰'},
    'spirituality': {'bg': '#EDE7F6', 'border': '#673AB7', 'icon': '🧘'},
    'contribution': {'bg': '#FBE9E7', 'border': '#FF5722', 'icon': '🤝'}
}

# Translations dictionary
TRANSLATIONS = {
    'pt': {
        'welcome': 'Bem-vindo ao Your Routine!',
        'login': 'Entrar',
        'signup': 'Criar Conta',
        'username': 'Usuário',
        'password': 'Senha',
        'confirm_password': 'Confirmar Senha',
        'dashboard': 'Dashboard',
        'your_routine': 'Seu Quadro',
        'settings': 'Configurações',
        'help': 'Ajuda',
        'logout': 'Sair',
        'add_event': 'Adicionar Evento',
        'category': 'Categoria',
        'title': 'Título',
        'description': 'Descrição',
        'days': 'Dia(s)',
        'start_time': 'Hora de início',
        'end_time': 'Hora de término',
        'add': 'Adicionar',
        'cancel': 'Cancelar',
        'success': '✅ Evento adicionado com sucesso!',
        'error_required': 'Por favor, preencha todos os campos obrigatórios.',
        'error_password': 'As senhas não coincidem!',
        'error_password_length': 'A senha deve ter pelo menos 6 caracteres!',
        'error_username_exists': 'Nome de usuário já existe!',
        'success_account': 'Conta criada com sucesso! Faça login para continuar.',
        'error_login': 'Usuário ou senha incorretos!',
        'select_language': 'Selecione o idioma:',
        'monday': 'Segunda',
        'tuesday': 'Terça',
        'wednesday': 'Quarta',
        'thursday': 'Quinta',
        'friday': 'Sexta',
        'saturday': 'Sábado',
        'sunday': 'Domingo',
        'time': 'Horário',
        'self_assessment': "Autoavaliação - Onde Focar na sua Roda da Vida",
        'focus_areas': "Áreas de Foco",
        'save_assessment': "Salvar Autoavaliação",
        'assessment_saved': "Autoavaliação salva com sucesso!",
        'missions_challenges': "Missões e Desafios Sugeridos",
        'choose_focus_areas': "Escolha as áreas que você gostaria de focar mais",
        'select_priority_areas': "Selecione as áreas que você considera prioritárias para melhorar",
        'mission_for': "Missão para",
        'need_more_time': "Dedique mais tempo para esta área, você está dedicando menos tempo do que o ideal!",
        'suggestion': "Sugestão",
        'add_activities': "Adicione algumas atividades desta área no seu quadro de rotina.",
        'doing_well': "Você está se dedicando adequadamente a esta área, continue assim!",
        'leisure': "Lazer",
        'career': "Carreira",
        'health': "Saúde",
        'relationships': "Relacionamentos",
        'personal_development': "Desenvolvimento Pessoal",
        'finances': "Finanças",
        'spirituality': "Espiritualidade",
        'contribution': "Contribuição",
        'leisure_time': "Quanto tempo você dedica a atividades de lazer por dia?",
        'leisure_satisfaction': "Você se sente suficientemente relaxado e descansado no seu tempo livre?",
        'career_time': "Quanto tempo você dedica ao trabalho por dia?",
        'career_balance': "Você está satisfeito com o equilíbrio entre sua vida profissional e pessoal?",
        'health_time': "Quanto tempo você dedica à sua saúde por semana?",
        'health_satisfaction': "Você está satisfeito com o tempo dedicado à sua saúde?",
        'relationships_time': "Quanto tempo você dedica para fortalecer seus relacionamentos por dia?",
        'relationships_satisfaction': "Você se sente satisfeito com seus relacionamentos?",
        'personal_development_time': "Quanto tempo você dedica ao seu desenvolvimento pessoal por dia?",
        'personal_development_progress': "Você está satisfeito com seu progresso pessoal?",
        'finances_time': "Você dedica tempo para planejar e acompanhar suas finanças pessoais por semana?",
        'finances_control': "Você sente que está no controle da sua saúde financeira?",
        'spirituality_time': "Você dedica tempo para sua prática espiritual por dia?",
        'spirituality_connection': "Você se sente bem conectado com seus valores e propósitos?",
        'contribution_time': "Você dedica tempo para ajudar os outros ou contribuir com sua comunidade por semana?",
        'contribution_satisfaction': "Você sente que está fazendo uma diferença positiva no mundo ao seu redor?",
        'no_time': "Nenhum tempo",
        'ideal_time': "Tempo ideal",
        'not_relaxed': "Nada relaxado",
        'fully_relaxed': "Totalmente relaxado",
        'not_satisfied': "Nada satisfeito",
        'fully_satisfied': "Totalmente satisfeito",
        'no_control': "Nenhum controle",
        'full_control': "Controle total",
        'not_connected': "Nada conectado",
        'fully_connected': "Totalmente conectado",
        'no_difference': "Nenhuma diferença",
        'big_difference': "Grande diferença",
        'edit_event': 'Editar Evento',
        'update': 'Atualizar',
        'remove': 'Remover',
        'update_success': '✅ Evento atualizado com sucesso!',
        'remove_success': '✅ Evento removido com sucesso!',
        'error_saving': 'Erro ao salvar o evento.',
        'error_removing': 'Erro ao remover o evento.',
        'career_satisfaction': "Você está satisfeito com sua carreira?",
        'health_satisfaction': "Você está satisfeito com sua saúde?",
        'relationships_satisfaction': "Você está satisfeito com seus relacionamentos?",
        'personal_development_satisfaction': "Você está satisfeito com seu desenvolvimento pessoal?",
        'finances_satisfaction': "Você está satisfeito com sua situação financeira?",
        'spirituality_satisfaction': "Você está satisfeito com sua vida espiritual?",
        'contribution_satisfaction': "Você está satisfeito com sua contribuição para a sociedade?",
        'error_time': 'O horário de término deve ser depois do horário de início.'
    },
    'en': {
        'welcome': 'Welcome to Your Routine!',
        'login': 'Login',
        'signup': 'Sign Up',
        'username': 'Username',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'dashboard': 'Dashboard',
        'your_routine': 'Your Schedule',
        'settings': 'Settings',
        'help': 'Help',
        'logout': 'Logout',
        'add_event': 'Add Event',
        'category': 'Category',
        'title': 'Title',
        'description': 'Description',
        'days': 'Day(s)',
        'start_time': 'Start Time',
        'end_time': 'End Time',
        'add': 'Add',
        'cancel': 'Cancel',
        'success': '✅ Event added successfully!',
        'error_required': 'Please fill in all required fields.',
        'error_password': 'Passwords do not match!',
        'error_password_length': 'Password must be at least 6 characters long!',
        'error_username_exists': 'Username already exists!',
        'success_account': 'Account created successfully! Please login to continue.',
        'error_login': 'Invalid username or password!',
        'select_language': 'Select language:',
        'monday': 'Monday',
        'tuesday': 'Tuesday',
        'wednesday': 'Wednesday',
        'thursday': 'Thursday',
        'friday': 'Friday',
        'saturday': 'Saturday',
        'sunday': 'Sunday',
        'time': 'Time',
        'self_assessment': "Self-Assessment - Where to Focus on your Wheel of Life",
        'focus_areas': "Focus Areas",
        'save_assessment': "Save Assessment",
        'assessment_saved': "Assessment saved successfully!",
        'missions_challenges': "Suggested Missions and Challenges",
        'choose_focus_areas': "Choose the areas you would like to focus more on",
        'select_priority_areas': "Select the areas you consider priority for improvement",
        'mission_for': "Mission for",
        'need_more_time': "Dedicate more time to this area, you are spending less time than ideal!",
        'suggestion': "Suggestion",
        'add_activities': "Add some activities from this area to your routine board.",
        'doing_well': "You are dedicating yourself adequately to this area, keep it up!",
        'leisure': "Leisure",
        'career': "Career",
        'health': "Health",
        'relationships': "Relationships",
        'personal_development': "Personal Development",
        'finances': "Finances",
        'spirituality': "Spirituality",
        'contribution': "Contribution",
        'leisure_time': "How much time do you dedicate to leisure activities per day?",
        'leisure_satisfaction': "Do you feel sufficiently relaxed and rested in your free time?",
        'career_time': "How much time do you dedicate to work per day?",
        'career_balance': "Are you satisfied with your work-life balance?",
        'health_time': "How much time do you dedicate to your health per week?",
        'health_satisfaction': "Are you satisfied with your health?",
        'relationships_time': "How much time do you dedicate to strengthening your relationships per day?",
        'relationships_satisfaction': "Are you satisfied with your relationships?",
        'personal_development_time': "How much time do you dedicate to your personal development per day?",
        'personal_development_progress': "Are you satisfied with your personal progress?",
        'finances_time': "Do you dedicate time to plan and track your personal finances per week?",
        'finances_control': "Do you feel in control of your financial health?",
        'spirituality_time': "Do you dedicate time to your spiritual practice per day?",
        'spirituality_connection': "Do you feel well connected with your values and purposes?",
        'contribution_time': "Do you dedicate time to helping others or contributing to your community per week?",
        'contribution_satisfaction': "Do you feel you are making a positive difference in the world around you?",
        'no_time': "No time",
        'ideal_time': "Ideal time",
        'not_relaxed': "Not relaxed",
        'fully_relaxed': "Fully relaxed",
        'not_satisfied': "Not satisfied",
        'fully_satisfied': "Fully satisfied",
        'no_control': "No control",
        'full_control': "Full control",
        'not_connected': "Not connected",
        'fully_connected': "Fully connected",
        'no_difference': "No difference",
        'big_difference': "Big difference",
        'edit_event': 'Edit Event',
        'update': 'Update',
        'remove': 'Remove',
        'update_success': '✅ Event updated successfully!',
        'remove_success': '✅ Event removed successfully!',
        'error_saving': 'Error saving the event.',
        'error_removing': 'Error removing the event.',
        'career_satisfaction': "Are you satisfied with your career?",
        'health_satisfaction': "Are you satisfied with your health?",
        'relationships_satisfaction': "Are you satisfied with your relationships?",
        'personal_development_satisfaction': "Are you satisfied with your personal development?",
        'finances_satisfaction': "Are you satisfied with your financial situation?",
        'spirituality_satisfaction': "Are you satisfied with your spiritual life?",
        'contribution_satisfaction': "Are you satisfied with your contribution to society?",
        'error_time': 'End time must be after start time.'
    }
}

def get_text(key):
    lang = session.get('language', 'pt')
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'][key])

# Create database tables
with app.app_context():
    db.create_all()

# Authentication routes
@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    return render_template('login.html', get_text=get_text)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['logged_in'] = True
        session['username'] = username
        session['user_id'] = user.id
        session['language'] = user.language
        flash(get_text('success_account'), 'success')
        return redirect(url_for('dashboard'))
    
    flash(get_text('error_login'), 'error')
    return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not username or not password:
        flash(get_text('error_required'), 'error')
        return redirect(url_for('index'))
    
    if password != confirm_password:
        flash(get_text('error_password'), 'error')
        return redirect(url_for('index'))
    
    if len(password) < 6:
        flash(get_text('error_password_length'), 'error')
        return redirect(url_for('index'))
    
    if User.query.filter_by(username=username).first():
        flash(get_text('error_username_exists'), 'error')
        return redirect(url_for('index'))
    
    user = User(
        username=username,
        password=generate_password_hash(password),
        language=session.get('language', 'pt')
    )
    db.session.add(user)
    db.session.commit()
    
    flash(get_text('success_account'), 'success')
    return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

# Main application routes
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    assessments = Assessment.query.filter_by(user_id=user.id).order_by(Assessment.assessment_date.desc()).first()
    
    assessment_data = {}
    if assessments:
        assessment_data = {
            'time': assessments.time,
            'satisfaction': assessments.satisfaction
        }
    
    return render_template('dashboard.html', 
                         assessment_data=assessment_data,
                         focus_areas=session.get('focus_areas', []),
                         get_text=get_text)

@app.route('/routine')
def routine():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    activities = Activity.query.filter_by(user_id=user.id).all()
    
    for activity in activities:
        activity.category_colors = CATEGORY_COLORS.get(activity.category, {})
    
    return render_template('routine.html', 
                         activities=activities,
                         category_colors=CATEGORY_COLORS,
                         get_text=get_text)

@app.route('/settings')
def settings():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    return render_template('settings.html', get_text=get_text)

@app.route('/help')
def help():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    return render_template('help.html', get_text=get_text)

# API routes
@app.route('/change_language', methods=['POST'])
def change_language():
    language = request.form.get('language')
    if language in ['pt', 'en']:
        session['language'] = language
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            user.language = language
            db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/update_password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password_hash(user.password, current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('settings'))
    
    if new_password != confirm_password:
        flash(get_text('error_password'), 'error')
        return redirect(url_for('settings'))
    
    if len(new_password) < 6:
        flash(get_text('error_password_length'), 'error')
        return redirect(url_for('settings'))
    
    user.password = generate_password_hash(new_password)
    db.session.commit()
    
    flash('Password updated successfully', 'success')
    return redirect(url_for('settings'))

@app.route('/save_activity', methods=['POST'])
def save_activity():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    activity_id = request.form.get('activity_id')
    title = request.form.get('title')
    category = request.form.get('category')
    description = request.form.get('description')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    days = request.form.getlist('days')
    
    if not all([title, category, start_time, end_time, days]):
        flash(get_text('error_required'), 'error')
        return redirect(url_for('routine'))
    
    try:
        if activity_id:
            # Update existing activity
            activity = Activity.query.get(activity_id)
            if activity and activity.user_id == session['user_id']:
                activity.title = title
                activity.category = category
                activity.description = description
                activity.start_time = start_time
                activity.end_time = end_time
                activity.day = days[0]  # For now, we only support one day per activity
        else:
            # Create new activities for each selected day
            for day in days:
                activity = Activity(
                    user_id=session['user_id'],
                    title=title,
                    category=category,
                    description=description,
                    start_time=start_time,
                    end_time=end_time,
                    day=day
                )
                db.session.add(activity)
        
        db.session.commit()
        flash(get_text('success'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(get_text('error_saving'), 'error')
    
    return redirect(url_for('routine'))

@app.route('/get_activity/<int:activity_id>')
def get_activity(activity_id):
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    activity = Activity.query.get(activity_id)
    if activity and activity.user_id == session['user_id']:
        return jsonify({
            'id': activity.id,
            'title': activity.title,
            'category': activity.category,
            'description': activity.description,
            'start_time': activity.start_time,
            'end_time': activity.end_time,
            'days': [activity.day]
        })
    return jsonify({'success': False})

@app.route('/delete_activity/<int:activity_id>')
def delete_activity(activity_id):
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    activity = Activity.query.get(activity_id)
    if activity and activity.user_id == session['user_id']:
        try:
            db.session.delete(activity)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False})
    return jsonify({'success': False})

@app.route('/save_assessment', methods=['POST'])
def save_assessment():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    user = User.query.get(session['user_id'])
    areas = ['leisure', 'career', 'health', 'relationships', 
             'personal_development', 'finances', 'spirituality', 'contribution']
    
    try:
        # Delete previous assessments
        Assessment.query.filter_by(user_id=user.id).delete()
        
        # Save new assessments
        for area in areas:
            time = int(request.form.get(f'{area}_time', 0))
            satisfaction = int(request.form.get(f'{area}_satisfaction', 0))
            
            assessment = Assessment(
                user_id=user.id,
                area=area,
                time=time,
                satisfaction=satisfaction
            )
            db.session.add(assessment)
        
        # Save focus areas
        focus_areas = request.form.getlist('focus_areas')
        session['focus_areas'] = focus_areas
        
        # Save assessment data for display
        assessment_data = {}
        for area in areas:
            assessment_data[area] = {
                'time': int(request.form.get(f'{area}_time', 0)),
                'satisfaction': int(request.form.get(f'{area}_satisfaction', 0))
            }
        session['assessment_data'] = assessment_data
        
        db.session.commit()
        flash(get_text('assessment_saved'), 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash('Error saving assessment', 'error')
        return jsonify({'success': False})

@app.route('/edit_activity/<int:activity_id>')
def edit_activity(activity_id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('index'))
    
    activity = Activity.query.get_or_404(activity_id)
    if activity.user_id != session['user_id']:
        return redirect(url_for('routine'))
    
    activities = Activity.query.filter_by(user_id=session['user_id']).all()
    
    # Add category colors to all activities
    for act in activities:
        act.category_colors = CATEGORY_COLORS.get(act.category, {})
    
    # Add category colors to the activity being edited
    activity.category_colors = CATEGORY_COLORS.get(activity.category, {})
    
    return render_template('routine.html', 
                         edit_activity=activity,
                         activities=activities,
                         category_colors=CATEGORY_COLORS,
                         get_text=get_text)

if __name__ == '__main__':
    app.run(debug=True) 