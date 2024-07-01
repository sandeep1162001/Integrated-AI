from flask import Flask, render_template, redirect, request, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

# Make Connection with Data Base
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'Bablu@12345'


# Create Database with the name of "User" 
class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = self.hash_password(password)

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ai_name = db.Column(db.String(100), nullable=False)
    img_name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(2048))
    description = db.Column(db.String(2000))
    
    user = db.relationship('User', backref=db.backref('bookmark', lazy=True))

    def __init__(self, user_id, ai_name, img_name, url, description):
        self.user_id = user_id
        self.ai_name = ai_name
        self.img_name = img_name
        self.url = url
        self.description = description
  
# Create Database with the name of "User"
class Contactus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(200))

    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message

with app.app_context():
    db.create_all()

#landing page
@app.route('/')
def startpage():
    return render_template('start.html', title='Home | Integrated AI')


# Home Page 
@app.route('/home')
def index():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('home.html', title='Home | Integrated AI')
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')

# New AI Lunched page
@app.route('/newai')
def newAi():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('newai.html', title='New AI')
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')
    

# Free AI page
@app.route('/freeai')
def freeAi():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('freeai.html', title='Free AI')
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')
    

# Paid AI page
@app.route('/paidai')
def paidAi():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('paidai.html', title=' Paid AI')
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')
    

#ContactUs Page
@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_contact = Contactus(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        flash('Message Sent Successfully.', 'success')
        return redirect('/contactus')
    return render_template('contactus.html', title='Contact Us')

#About Page
@app.route('/about')
def about():
    return render_template('about.html', title='About')

# Register Page 
@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use different email.', 'error')
            return redirect('/signup')  # Redirect back to registration page with flash message

        
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect('/signup')

    return render_template('signup.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/home')
        else:
            error = 'Invalid email or password. Please try again.'
            flash(error, 'error')

    return render_template('login.html')

#add ai page to bookmarks
@app.route('/addbookmark', methods=['GET', 'POST'])
def add():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if request.method == 'POST':
            ai_name = request.form['ai_name']
            img_name = request.form['img_name']
            url = request.form['url']
            description = request.form['description']
            
            # Check if the AI name already exists for this user
            existing_ai_page = Bookmark.query.filter_by(user_id=user.id, ai_name=ai_name).first()
            
            if not existing_ai_page:
                # Adding bookmark
                bookmark = Bookmark(user_id=user.id, ai_name=ai_name, img_name=img_name, url=url, description=description)
                db.session.add(bookmark)
                db.session.commit()
                flash('Bookmark added successfully!')
                return redirect('/bookmark')
            else:
                flash(' This AI is already exists in Bookmark.')
                return redirect('/bookmark')
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')
    
   
# Bookmark Page 
@app.route('/bookmark')
def bookmark():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        bookmark = Bookmark.query.filter_by(user_id=user.id).all()
        return render_template('bookmark.html', title='Bookmark', bookmarks=bookmark)
    else:
        flash('You need to login first.', 'error')
        return redirect('/login')
    

#Logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    # flash('You have been logged out.', 'info')
    return redirect('/')


#Here all web pages of A.I websites based on your work

# Webdev Page
@app.route('/webdev')
def webdev():
    img = 'web development.png'  # Replace with the actual filename or logic to determine the image
    title = 'Webdev'
    web_head = 'Webdev'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."

    return render_template('webdev.html', title=title, img=img,  web_head=web_head, description=description)

# Webdev Page
@app.route('/agriculture')
def agriculutre():
    img = 'web development.png'  # Replace with the actual filename or logic to determine the image
    title = 'Agriculutre'
    web_head = 'Agriculutre'
    description = " AI-enabled systems make weather predictions, monitor agricultural sustainability, and assess farms for the presence of diseases or pests and undernourished plants using data like temperature, precipitation, wind speed, and sun radiation in conjunction with photographs taken by satellites and drones.Agriculture is dependent on a number of variables, including soil nutrient content, moisture, crop rotation, rainfall, temperature, etc. Products based on artificial intelligence can use these variables to track crop productivity. In order to improve a wide range of agriculture-related tasks throughout the entire food supply chain, industries are turning to Artificial Intelligence technologies."

    return render_template('agriculutre.html', title=title, img=img,  web_head=web_head, description=description)

# Webdev Page
@app.route('/editing')
def editing():
    img = 'web development.png'  # Replace with the actual filename or logic to determine the image
    title = 'Editing'
    web_head = 'Editing'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."

    return render_template('editing.html', title=title, img=img,  web_head=web_head, description=description)

# Finance Page
@app.route('/finance')
def finance():
    img = 'finance-logo.jpg'  # Replace with the actual filename or logic to determine the image
    title = 'Finance'
    web_head = 'Finance'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."

    return render_template('finance.html', title=title, img=img,  web_head=web_head, description=description)

# Manufacturing Page
@app.route('/manufacturing')
def manufacturing():
    img = 'AI-In-Manufacturing-logo.jpg'  # Replace with the actual filename or logic to determine the image
    title = 'Manufacturing'
    web_head = 'Manufacturing'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."

    return render_template('manufacturing.html', title=title, img=img,  web_head=web_head, description=description)

# Painting Page
@app.route('/painting')
def painting():
    img = 'painting-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Painting'
    web_head = 'Painting'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."
    return render_template('painting.html', title=title, img=img,  web_head=web_head, description=description)

# retail Page
@app.route('/retail')
def retail():
    img = 'retail-logo.jpeg'  # Replace with the actual filename or logic to determine the image
    title = 'Retail'
    web_head = 'Retail'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."
    return render_template('retail.html', title=title, img=img,  web_head=web_head, description=description)

# Sports Page
@app.route('/sports')
def sports():
    img = 'sports-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Sports'
    web_head = 'Sports'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."
    return render_template('sports.html', title=title, img=img,  web_head=web_head, description=description)

# Transoprtation Page
@app.route('/transoprtation')
def transoprtation():
    img = 'transport-logo.jpg'  # Replace with the actual filename or logic to determine the image
    title = 'Transoprtation'
    web_head = 'Transoprtation'
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."
    return render_template('transoprtation.html', title=title, img=img,  web_head=web_head, description=description)


#  all AI websites pages
@app.route('/chatgpt')
def chatgpt():
    img = 'chatgpt logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'ChatGPT'
    web_head = 'ChatGPT'
    link = "https://chatgpt.com/"
    description = "We have trained a model called ChatGPT which interacts in a conversational way. The dialogue format makes it possible for ChatGPT to answer followup questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests. ChatGPT is a sibling model to InstructGPT, which is trained to follow an instruction in a prompt and provide a detailed response. We are excited to introduce ChatGPT to get users’ feedback and learn about its strengths and weaknesses. During the research preview, usage of ChatGPT is free."
    return render_template('chatgpt.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/blackboxai')
def blackboxai():
    img = 'blackboxai-logo-org.png'  # Replace with the actual filename or logic to determine the image
    title = 'BLACKBOX AI'
    web_head = 'BLACKBOX AI'
    link = "https://www.blackbox.ai/"
    description = "Blackbox AI is an AI-powered tool designed to assist developers in writing, generating, and optimizing code. It features advanced code completion, real-time knowledge integration, error identification, and version tracking. Blackbox AI supports over 20 programming languages and integrates with platforms like GitHub, making it a versatile and powerful companion for software development. It aims to increase productivity by providing contextual code suggestions, automating repetitive tasks, and facilitating better code management."
    return render_template('blackboxai.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/geminiai')
def geminiai():
    img = 'gemini-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Gemini'
    web_head = 'Gemini'
    link = "https://gemini.google.com/"
    description = "Gemini is Google's next-generation AI model, developed by DeepMind, which aims to combine the capabilities of large language models with advanced problem-solving abilities and multimodal integration. It is designed to enhance conversational AI by understanding and generating human-like text across various contexts. Gemini is expected to advance beyond the current state of AI models by integrating techniques from DeepMind's AlphaGo and AlphaFold projects, leveraging reinforcement learning, and incorporating knowledge from different modalities such as text, images, and possibly other data types. This integration aims to provide a more sophisticated and versatile AI that can tackle a wider range of tasks and applications."
    return render_template('geminiai.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/sourcery')
def sourcery():
    img = 'sourcery-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Sourcery'
    web_head = 'Sourcery'
    link = "https://sourcery.ai/"
    description = "Sourcery is a tool that automates code refactoring and suggests improvements in Python codebases. It analyzes code to identify potential optimizations,  refactorings, and best practices, helping developers write cleaner, more efficient code with fewer manual interventions. Sourcery integrates with popular code editors and version control systems,  streamlining the process of code review and enhancement directly within the developer's workflow."
    return render_template('sourcery.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/synk')
def synk():
    img = 'sourcery-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Synk'
    web_head = 'Synk'
    link = "https://snyk.io/"
    description = "Synk is a security platform designed to help developers and organizations manage open-source security risks in their codebases. It provides tools for identifying, prioritizing, and fixing vulnerabilities in dependencies used within applications. Synk integrates seamlessly into development workflows, offering automated security scans, real-time alerts, and actionable insights to mitigate security threats effectively. By monitoring and analyzing open-source components continuously, Synk enables teams to proactively protect their software from potential security breaches and ensure compliance with industry standards."
    return render_template('synk.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/tabnine')
def tabnine():
    img = 'tabnine-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Tabnine'
    web_head = 'Tabnine'
    link = "https://www.tabnine.com/"
    description = "Tabnine is an AI-powered code completion tool designed to accelerate programming workflows by providing intelligent code suggestions directly within integrated development environments (IDEs). It uses machine learning models trained on vast code repositories to offer context-aware completions, helping developers write code faster and with greater accuracy. Tabnine supports a wide range of programming languages and integrates seamlessly with popular IDEs like Visual Studio Code, IntelliJ IDEA, and more, enhancing productivity by reducing the time spent on manual typing and syntax lookup."
    return render_template('tabnine.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/github')
def github():
    img = 'github-logo.webp'  # Replace with the actual filename or logic to determine the image
    title = 'GitHub Copilot'
    web_head = 'GitHub Copilot'
    link = "https://github.com/features/copilot"
    description = "GitHub Copilot is an AI-powered code completion tool developed by GitHub in collaboration with OpenAI. It assists developers by suggesting whole lines or blocks of code as they type, making coding faster and more efficient. Integrated into Visual Studio Code, Copilot supports multiple programming languages and uses context from comments and code to provide relevant suggestions. It leverages OpenAI's Codex model to understand natural language prompts and generate corresponding code, significantly enhancing developer productivity by reducing the time spent on routine coding tasks."
    return render_template('github.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/intellicode')
def intellicode():
    img = 'intellicode-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Intellicode'
    web_head = 'Intellicode'
    link = "https://visualstudio.microsoft.com/services/intellicode/"
    description = "Intellicode is an AI-powered code suggestion feature developed by Microsoft for Visual Studio and Visual Studio Code. It enhances the coding experience by providing context-aware code completions and suggestions based on the current context in your code, leveraging machine learning models trained on large codebases. Intellicode helps developers write code faster and more accurately by prioritizing the most relevant suggestions, improving productivity and reducing the cognitive load associated with manual code completion."
    return render_template('intellicode.html', title=title, img=img, link=link,  web_head=web_head, description=description)

@app.route('/replit')
def replit():
    img = 'replit-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Replit'
    web_head = 'Replit'
    link = "https://replit.com/"
    description = "Replit is an online integrated development environment (IDE) that allows users to write, collaborate on, and deploy code directly from their web browser. It supports a wide range of programming languages and provides features like real-time collaboration, version control integration, and cloud-based hosting for projects. Replit is designed to simplify the coding experience, particularly for beginners and teams looking for an accessible platform to develop and share code projects efficiently."
    return render_template('replit.html', title=title, img=img, link=link,  web_head=web_head, description=description)



if __name__ == '__main__':
    app.run(debug=True)