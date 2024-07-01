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
    

# Dummy data
ai_websites = [
    {
        'name': 'Web Development',
        'description': 'AI web development tools use artificial intelligence to automate, improve, and streamline the web development process. They reduce manual coding efforts, optimize design elements.',
        'url': '/webdev',
        'image': 'web development.png'
    },
    {
        'name': 'Agriculture',
        'description': 'Artificial intelligence (AI) can help farmers make data-driven decisions to improve productivity and environmental outcomes.',
        'url': '/agriculture',
        'image': 'agriculture-logo.jpg'
    },
    {
        'name': 'Editing',
        'description': 'AI can help with editing by automating tasks and streamlining the process. AI tools can help with video and audio editing, photo editing, and more.',
        'url': '/editing',
        'image': 'editing logo.jpeg'
    },
    {
        'name': 'Finance',
        'description': 'AI can quickly analyze large volumes of data to identify trends and help forecast future performance, letting investors chart investment growth and evaluate potential risk.',
        'url': '/finance',
        'image': 'finance-logo.jpg'
    }
]

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').lower()
    results = [site for site in ai_websites if query in site['name'].lower() or query in site['description'].lower()]
    if not results:
        flash('No results found. Try searching for something else...', 'success')
        return render_template('home.html', query=query)
    else:
        return render_template('home.html', results=results, query=query,)


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
    description = " AI websites can significantly enhance the editing process by providing advanced tools that streamline and improve the quality of written content. These platforms use natural language processing algorithms to detect grammatical errors, suggest stylistic improvements, and ensure coherence and clarity. They can also offer synonyms and rephrasing options to enrich vocabulary and variety in writing. Additionally, AI editors can check for plagiarism, ensuring originality and proper citation of sources. By providing real-time feedback, these tools allow writers to refine their work efficiently, ultimately producing polished and professional documents."

    return render_template('editing.html', title=title, img=img,  web_head=web_head, description=description)

# Finance Page
@app.route('/finance')
def finance():
    img = 'finance-logo.jpg'  # Replace with the actual filename or logic to determine the image
    title = 'Finance'
    web_head = 'Finance'
    description = " AI websites can significantly enhance the finance sector by offering advanced data analytics, predictive modeling, and automated processes. These platforms can analyze vast amounts of financial data in real-time, providing insights that help investors make informed decisions. AI algorithms can predict market trends, detect fraudulent activities, and optimize trading strategies, thereby reducing risks and increasing returns. Additionally, AI-driven customer service tools can streamline interactions, offering personalized advice and support to clients. By automating routine tasks, AI websites free up financial professionals to focus on more complex and strategic activities, ultimately improving efficiency and productivity in the finance industry."

    return render_template('finance.html', title=title, img=img,  web_head=web_head, description=description)

# Manufacturing Page
@app.route('/manufacturing')
def manufacturing():
    img = 'AI-In-Manufacturing-logo.jpg'  # Replace with the actual filename or logic to determine the image
    title = 'Manufacturing'
    web_head = 'Manufacturing'
    description = " AI websites can significantly enhance the manufacturing sector by providing advanced tools and resources for optimizing processes, improving efficiency, and reducing costs. These platforms can offer real-time data analytics, predictive maintenance, and supply chain optimization, helping manufacturers to anticipate and address potential issues before they arise. Additionally, AI websites can facilitate automated quality control through machine learning algorithms that detect defects and ensure consistency in production. By leveraging the insights and capabilities provided by AI, manufacturers can streamline operations, increase productivity, and maintain a competitive edge in the market."

    return render_template('manufacturing.html', title=title, img=img,  web_head=web_head, description=description)

# Painting Page
@app.route('/painting')
def painting():
    img = 'painting-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Painting'
    web_head = 'Painting'
    description = "AI websites can significantly aid in painting by providing artists with innovative tools and resources to enhance their creativity and efficiency. These platforms often feature advanced algorithms that can generate color palettes, suggest composition improvements, and even create entire paintings based on input parameters. Artists can upload their work to receive real-time feedback and suggestions for enhancements, helping them refine their techniques. Additionally, AI-powered websites can offer tutorials, style transfer capabilities, and virtual brushes that mimic various traditional media, allowing artists to experiment with different styles and techniques without the need for physical materials. By integrating AI into the creative process, artists can explore new possibilities, save time, and push the boundaries of their artistic expression."
    return render_template('painting.html', title=title, img=img,  web_head=web_head, description=description)

# retail Page
@app.route('/retail')
def retail():
    img = 'retail-logo.jpeg'  # Replace with the actual filename or logic to determine the image
    title = 'Retail'
    web_head = 'Retail'
    description = " AI-powered websites can revolutionize the retail industry by enhancing customer experiences and streamlining operations. Through advanced algorithms, these platforms can personalize shopping experiences by recommending products based on individual preferences and browsing history. AI chatbots provide instant customer support, addressing inquiries and resolving issues efficiently. Additionally, AI can optimize inventory management by predicting demand trends, reducing overstock and stockouts. Retailers can also leverage AI for dynamic pricing strategies, adjusting prices in real-time based on market conditions and competitor actions. Overall, AI websites enable retailers to improve customer satisfaction, increase sales, and operate more efficiently."
    return render_template('retail.html', title=title, img=img,  web_head=web_head, description=description)

# Sports Page
@app.route('/sports')
def sports():
    img = 'sports-logo.png'  # Replace with the actual filename or logic to determine the image
    title = 'Sports'
    web_head = 'Sports'
    description = "AI websites can significantly enhance the sports industry by offering a range of advanced analytics, real-time data, and personalized experiences for fans, athletes, and teams. These platforms can analyze vast amounts of data to provide insights into player performance, game strategies, and injury prevention, helping coaches and players make more informed decisions. For fans, AI can curate personalized content, such as highlight reels, game predictions, and interactive experiences, enhancing their engagement and enjoyment. Additionally, AI-driven platforms can assist in sports betting by providing accurate predictions and odds, ensuring a more informed and responsible gambling experience. Overall, AI websites serve as powerful tools to elevate the efficiency, excitement, and understanding of sports."
    return render_template('sports.html', title=title, img=img,  web_head=web_head, description=description)

# Transoprtation Page
@app.route('/transoprtation')
def transoprtation():
    img = 'transport-logo.jpg'  # Replace with the actual filename or logic to determine the image
    title = 'Transoprtation'
    web_head = 'Transoprtation'
    description = "AI websites can revolutionize transportation by offering real-time data analysis and predictive insights. These platforms can optimize traffic management by analyzing traffic patterns and suggesting alternative routes, reducing congestion and travel time. They can enhance public transportation by predicting peak usage times and adjusting schedules accordingly. For logistics and delivery services, AI websites can plan the most efficient routes, cutting down on fuel consumption and delivery times. Additionally, they can improve safety by monitoring vehicle conditions and alerting for maintenance needs before they become critical. Overall, AI websites provide a smart, efficient, and proactive approach to managing and improving transportation systems."
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