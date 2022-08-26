from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User, Note, Classgroup, Books, Bookreq, Tags, Booktags, Ratings
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from AskMissy_Test import website_algorithm
from AskMissy_Test import output


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usertype = request.form.get('usertype')
        email = request.form.get('email')
        password = request.form.get('password')
        print(usertype)
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

        #session["user"] = '1'

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        usertype = request.form.get('usertype')
        email = request.form.get('email')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        school = request.form.get('school')
        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(fname) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(user_type=usertype, email=email, first_name=fname, last_name=lname,
                            password=generate_password_hash(password1, method='sha256'), school=school)
            db.session.add(new_user)
            db.session.commit()
            #login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/browse', methods=['GET', 'POST'])
def browse():
    tag_lists = []
    if request.method == 'POST':
        title = request.form.get('bookTitle')
        author = request.form.get('author')
        year = request.form.get('year')
        tag = request.form.get('tag')
        search1 = "%{}%".format(title)
        search2 = "%{}%".format(author)
        search3 = "%{}%".format(year)

        first_book = 0
        second_book = 0
        no_second = False
        no_tag = False
        print(tag)
        if tag:

            search4 = tag.replace(" ", "-").lower()
            print(search4)
            tagged_book = Tags.query.filter_by(tag_name=search4).first()
            print(tagged_book)
            if not tagged_book:
                no_tag = True
                tag_lists = []
            else:
                tag_list = Booktags.query.filter_by(tag_id=tagged_book.tag_id).all()
                print("I am here")
                for i in tag_list:
                    tag_lists.append(i.book_id)

            book_title = Books.query.filter(Books.title.like(search1),
                                            Books.authors.like(search2),
                                            Books.original_publication_year.like(search3),
                                            Books.goodreads_book_id.in_(tag_lists)
                                            ).all()
            for z in book_title:
                print(z.title)
        else:
            book_title = Books.query.filter(Books.title.like(search1),
                                            Books.authors.like(search2),
                                            Books.original_publication_year.like(search3),
                                            ).all()

        first_id = request.form.get('book_id')
        if first_id:
            second_id = website_algorithm.book_recommendation(first_id)
            if second_id == -1:
                no_second = True
            first_book = Books.query.filter_by(book_id = first_id).first()
            second_book = Books.query.filter_by(book_id = second_id).first()
        rate_id = request.form.get('book_id2')
        rate_score = request.form.get('score')
        if rate_id and rate_score:
            rating = Ratings(user_id=current_user.id, book_id=rate_id, rating=rate_score)
            past_rating = Ratings.query.filter(Ratings.user_id==current_user.id, Ratings.book_id==rate_id).first()
            if past_rating:
                db.session.delete(past_rating)
                db.session.commit()
            db.session.add(rating)
            db.session.commit()

        return render_template("browse.html", user=current_user, book=book_title, title=title, author=author, year=year,
                               tag=tag, first=first_book, second=second_book, no_second=no_second)
    else:
        # book_title = Book.query.filter_by(title='The Great Gatsby').first()
        return render_template("browse.html", user=current_user)


@auth.route('/settings', methods=['GET', 'POST'])
def settings():
    email = current_user.email
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    password3 = request.form.get('password3')

    user = User.query.filter_by(email=email).first()
    if user:
        if password:
            if check_password_hash(user.password, password):
                if password2:
                    if password2 == password3:
                        password1 = generate_password_hash(password2, method='sha256')
                        user.password = password1
                        db.session.commit()
        elif fname != None:
            user.fname = fname
            db.session.commit()
        elif lname != None:
            user.lname = lname
            db.session.commit()
        flash('Settings changed!', category='success')

    return render_template("settings.html", user=current_user)


@auth.route('/teacherProfile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        class_name = request.form.get('classname')
        class_num = request.form.get('classnum')
        teacher = current_user.first_name + ' ' + current_user.last_name
        classgroup = Classgroup.query.filter_by(class_num=class_num).first()

        if classgroup:
            flash('Class pin already exists.', category='error')
        elif len(class_num) < 4:
            flash('class number must be greater than 3 characters.', category='error')
        else:
            new_classgroup = Classgroup(class_name=class_name, class_num=class_num, teacher=teacher,
                                        user_id=current_user.id)
            db.session.add(new_classgroup)
            db.session.commit()
            #login_user(user, remember=True)
            flash('classgroup created!', category='success')

    return render_template("teacherProfile.html", user=current_user)


@auth.route('/resourcereq', methods=['GET', 'POST'])
def resourcereq():
    if request.method == 'POST':
        title = request.form.get('resourceName')
        author = request.form.get('author')
        publication = request.form.get('year')
        isbn = request.form.get('isbn')

        book = Books.query.filter_by(isbn=isbn).first()
        bookreq = Bookreq.query.filter_by(isbn=isbn).first()

        if book:
            flash('Book already in AskMissy.', category='error')
        elif bookreq:
            flash('Book already being requested', category='error')
        else:
            new_book = Bookreq(title=title, authors=author, publication_data=publication, isbn=isbn)
            db.session.add(new_book)
            db.session.commit()
            flash('Book added!', category='success!')
    return render_template("resourcereq.html", user=current_user)


@auth.route('/analytics')
def analytics():
    return render_template("analytics.html", user=current_user)


@auth.route('/inventory')
def inventory():
    return render_template("inventory.html", user=current_user)


@auth.route('/schoolgroup')
def schoolgroup():
    classinfo = []
    for i in range(9999):
        i2 = str(i+1)
        if i < 10:
            num = '000' + i2
        elif 10 <= i < 100:
            num = '00' + i2
        elif 100 <= i < 1000:
            num = '0' + i2
        else:
            num = i2
        if Classgroup.query.filter_by(class_num=num).first() != None:
            test = Classgroup.query.filter_by(class_num=num).first()

            classname = test.class_name
            teacher = 'Prof. ' + test.teacher

            classinfo_cn = [classname]
            classinfo_t = [teacher]
            classinfo += classinfo_cn + classinfo_t

            test = Classgroup.query.filter_by(class_num=num).all()
            print(test)
            for x in test:
                user = x.user_id
                student = User.query.filter_by(id=user).first()
                if (student.first_name + ' ' + student.last_name) != x.teacher:
                    studentname = student.first_name + ' ' + student.last_name
                    classinfo_s = [studentname]
                    classinfo += classinfo_s

    return render_template("schoolgroup.html", classinfo=classinfo, user=current_user)


@auth.route('/orders', methods=['GET', 'POST'])
def orders():
    books = Bookreq.query.filter(Bookreq.id).all()
    if request.method == 'POST':
        if request.form['Sendrequests'] == 'Sendrequests':
            for book in books:
                title = book.title
                author = book.authors
                publication = book.publication_data
                isbn = book.isbn

                print(title, author, publication, isbn)
                new_book = Books(title=title, authors=author, original_publication_year=publication, isbn=isbn)
                db.session.add(new_book)
                db.session.commit()
                db.session.delete(book)
                db.session.commit()
    if books != None:
        return render_template("orders.html", user=current_user, books=books)
    else:
        return render_template("orders.html", user=current_user)


@auth.route('/studentProfile', methods=['GET', 'POST'])
def studentProfile():
    if request.method == 'POST':
        class_num = request.form.get('classnum')

        classgroup = Classgroup.query.filter_by(class_num=class_num).first()

        if len(class_num) < 4:
            flash('class number must be greater than 3 characters.', category='error')
        elif classgroup == None:
            flash('class does not exist', category='error')
        else:
            new_classgroup = Classgroup(class_name=classgroup.class_name, class_num=class_num, teacher=classgroup.teacher,
                                        user_id=current_user.id)
            db.session.add(new_classgroup)
            db.session.commit()
            #login_user(user, remember=True)
            flash('Joined Class!', category='success')

    noteinfo = []
    notes2 = Classgroup.query.filter(Classgroup.user_id==current_user.id).all()
    for x in notes2:
        classname = x.class_name
        notes = Note.query.filter(Note.class_color==classname).all()
        noteinfo += notes


    return render_template("studentProfile.html", user=current_user, notes=noteinfo)


@auth.route('/english', methods=['GET', 'POST'])
def redGroup():
    if request.method == 'POST':
        note = request.form.get('note')
        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='English')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "English").all()

    return render_template("english.html", user=current_user, notes=notes)


@auth.route('/calculus', methods=['GET', 'POST'])
def blueGroup():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Calculus')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Calculus").all()

    return render_template("calculus.html", user=current_user, notes=notes)


@auth.route('/chemistry', methods=['GET', 'POST'])
def greenGroup():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Chemistry')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Chemistry").all()

    return render_template("chemistry.html", user=current_user, notes=notes)


@auth.route('/geology', methods=['GET', 'POST'])
def yellowGroup():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Geology')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Geology").all()

    return render_template("geology.html", user=current_user, notes=notes)


@auth.route('/physics', methods=['GET', 'POST'])
def physics():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Physics')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Physics").all()

    return render_template("physics.html", user=current_user, notes=notes)


@auth.route('/precalculus', methods=['GET', 'POST'])
def precalculus():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Precalculus')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Precalculus").all()

    return render_template("precalculus.html", user=current_user, notes=notes)


@auth.route('/programming', methods=['GET', 'POST'])
def programming():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Programming')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Programming").all()

    return render_template("programming.html", user=current_user, notes=notes)


@auth.route('/science', methods=['GET', 'POST'])
def science():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Science')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Science").all()

    return render_template("science.html", user=current_user, notes=notes)


@auth.route('/ushistory', methods=['GET', 'POST'])
def ushistory():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='US History')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "US History").all()

    return render_template("ushistory.html", user=current_user, notes=notes)


@auth.route('/worldhistory', methods=['GET', 'POST'])
def worldhistory():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='World History')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "World History").all()

    return render_template("worldhistory.html", user=current_user, notes=notes)


@auth.route('/math', methods=['GET', 'POST'])
def math():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Math')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Math").all()

    return render_template("math.html", user=current_user, notes=notes)


@auth.route('/literature', methods=['GET', 'POST'])
def literature():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Literature')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Literature").all()

    return render_template("literature.html", user=current_user, notes=notes)


@auth.route('/biology', methods=['GET', 'POST'])
def biology():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Biology')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Biology").all()

    return render_template("biology.html", user=current_user, notes=notes)


@auth.route('/algebra', methods=['GET', 'POST'])
def algebra():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='Algebra')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "Algebra").all()

    return render_template("algebra.html", user=current_user, notes=notes)


@auth.route('/history', methods=['GET', 'POST'])
def history():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id, class_color='History')
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    notes = Note.query.filter(Note.class_color == "History").all()

    return render_template("history.html", user=current_user, notes=notes)



@auth.route('/classgroup', methods=['GET', 'POST'])
def classgroup():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Announcement is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Announcement added!', category='success!')

    return render_template("classgroup.html", user=current_user)


@auth.route('/messages')
def messages():
    return render_template("messages.html", user=current_user)


@auth.route('/teacherMessages')
def teacherMessages():
    return render_template("teacherMessages.html", user=current_user)


@auth.route('/homeSample')
def homeSample():
    return render_template("homeSample.html", user=current_user)


@auth.route('/Contact')
def contact():
    return render_template("Contact.html", user=current_user)


@auth.route('/About')
def about():
    return render_template("About.html", user=current_user)


@auth.route('/home')
def home():
    return render_template("home.html", user=current_user)

@auth.route('/myrec' ,methods=['GET', 'POST'])
def myrec():
    print("hello world")
    # call the reader's past books for viewing
    new_book_list = []
    read_list1 = []

    read_list2 = Ratings.query.filter_by(user_id=current_user.id).all()
    for i in read_list2:
        read_list1.append(i.book_id)
    book_list1 = Books.query.filter(Books.book_id.in_(read_list1)).all()
    group_table = Books.query.join(Ratings, Books.book_id==Ratings.book_id)\
        .add_columns(Books.book_id, Books.title, Books.authors, Books.original_publication_year, Ratings.rating, Books.isbn)\
        .filter(Books.book_id==Ratings.book_id).filter(Ratings.user_id==current_user.id).all()

    # generate recommendations
    tag_entered = False
    if request.method == 'POST':
        tag_search = 0
        tag = request.form.get('tag')
        tag_entered = True
        tag_fix = tag.replace(" ", "-").lower()
        tag_search = Tags.query.filter_by(tag_name=tag_fix).first()
        print(tag_search)
        if not tag_search:
            new_book_list = []
        else:
            new_book_list = website_algorithm.findUser_website(current_user.id, tag_search.tag_id)
        new_books = Books.query.filter(Books.book_id.in_(new_book_list)).all()
    if tag_entered:
        return render_template("myrec.html", user=current_user, past=group_table, future=new_books, genre=tag_fix)
    else:
        return render_template("myrec.html", user=current_user, past=group_table)
