from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, IntegerField, HiddenField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', 
                             validators=[DataRequired(), 
                                        Length(min=6)])
    confirm_password = PasswordField(
        'Confirm New Password', 
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(),
                                        EqualTo('password')])
    submit = SubmitField('Register')


class ProfileForm(FlaskForm):
    # Personal Information
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Mobile Number (10 digits)', validators=[DataRequired()])
    
    # Address Information
    country = SelectField('Country', validators=[DataRequired()], choices=[('india', 'India')])
    state = SelectField('State', validators=[DataRequired()], choices=[
        ('', 'Select State'),
        ('andhra_pradesh', 'Andhra Pradesh'),
        ('telangana', 'Telangana'),
        ('karnataka', 'Karnataka'),
        ('tamil_nadu', 'Tamil Nadu'),
        ('maharashtra', 'Maharashtra'),
        ('delhi', 'Delhi'),
        ('uttar_pradesh', 'Uttar Pradesh')
    ])
    city = StringField('City/District/Town', validators=[DataRequired()])
    zipcode = StringField('Pin Code', validators=[DataRequired()])
    locality = StringField('Locality', validators=[DataRequired()])
    address = TextAreaField('Address (Area and Street)', validators=[DataRequired()])
    
    submit = SubmitField('Update Profile')


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price',
                       validators=[DataRequired(),
                                   NumberRange(min=0)])
    stock = IntegerField('Stock',
                         validators=[DataRequired(),
                                     NumberRange(min=0)])
    category = SelectField('Category',
                           choices=[('cpu', 'CPU'), ('gpu', 'GPU'),
                                    ('motherboard', 'Motherboard'),
                                    ('ram', 'RAM'), ('storage', 'Storage'),
                                    ('psu', 'Power Supply'),
                                    ('case', 'Cabinet'),
                                    ('cooling', 'Cooling'),
                                    ('peripherals', 'Peripherals'),
                                    ('monitor', 'Monitor'),
                                    ('prebuilt_intel', 'Prebuilt PC - Intel'),
                                    ('prebuilt_amd', 'Prebuilt PC - AMD')])
    image_url = StringField('Image URL', validators=[DataRequired()])
    featured = BooleanField('Featured Product')
    specs = TextAreaField('Specifications (JSON)', validators=[Optional()])
    submit = SubmitField('Add Product')


class CheckoutForm(FlaskForm):
    # Personal Information
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Mobile Number (10 digits)', validators=[DataRequired()])
    alt_phone = StringField('Alternate Phone (Optional)')
    
    # Address Information
    country = SelectField('Country', validators=[DataRequired()], choices=[('india', 'India')])
    state = SelectField('State', validators=[DataRequired()], choices=[
        ('', 'Select State'),
        ('andhra_pradesh', 'Andhra Pradesh'),
        ('telangana', 'Telangana'),
        ('karnataka', 'Karnataka'),
        ('tamil_nadu', 'Tamil Nadu'),
        ('maharashtra', 'Maharashtra'),
        ('delhi', 'Delhi'),
        ('uttar_pradesh', 'Uttar Pradesh')
    ])
    city = StringField('City/District/Town', validators=[DataRequired()])
    zipcode = StringField('Pin Code', validators=[DataRequired()])
    locality = StringField('Locality', validators=[DataRequired()])
    address = TextAreaField('Address (Area and Street)', validators=[DataRequired()])
    landmark = StringField('Landmark (Optional)')
    
    # Address Type
    address_type = RadioField('Address Type', 
                             choices=[('home', 'Home (All day delivery)'),
                                     ('work', 'Work (Delivery between 10 AM - 5 PM)')],
                             validators=[DataRequired()],
                             default='home')
    
    # Payment Method
    payment_method = RadioField('Payment Method',
                                choices=[('credit_card', 'Credit Card'),
                                         ('debit_card', 'Debit Card'),
                                         ('net_banking', 'Net Banking'),
                                         ('upi', 'UPI'),
                                         ('cod', 'Cash on Delivery')],
                                validators=[DataRequired()])
    
    submit = SubmitField('Save and Deliver Here')


class PaymentForm(FlaskForm):
    card_number = StringField('Card Number', validators=[Optional()])
    card_holder = StringField('Card Holder Name', validators=[Optional()])
    expiration_month = SelectField('Month',
                                   choices=[(str(i), str(i).zfill(2))
                                            for i in range(1, 13)],
                                   validators=[Optional()])
    expiration_year = SelectField('Year',
                                  choices=[(str(i), str(i))
                                           for i in range(2023, 2034)],
                                  validators=[Optional()])
    cvv = StringField('CVV', validators=[Optional()])
    submit = SubmitField('Pay Now')
