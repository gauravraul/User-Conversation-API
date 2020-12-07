import jwt                                  
import uuid                                 
from flask import Flask, request,session    
from flask import jsonify                   
from functools import wraps                 
import json                                 
import datetime                             


chatbot = Flask(__name__)

chatbot.config['SECRET_KEY'] = 'DoNotShareThisKey3000'


def only_token_access(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'token' in request.headers:
            token = request.headers['token']

        if not token:
            session.clear()
            response = jsonify({'Error' : 'Please Add Your Mobile Number and Token associated with it!!!'}), 401
            return response

        try: 
            data = jwt.decode(token, chatbot.config['SECRET_KEY'])
            mobile_number= data['mobile_number']
            
            if session['user_details']['mobile_number']!= mobile_number:
                session.clear()
                response = jsonify({'Error' : 'Please Add Your Mobile Number and Token associated with it!!!'}), 401
                return response
        except:
            session.clear()
            response = jsonify({'Error' : 'Please Add Your Mobile Number and Token associated with it!!!'}), 401
            return response

        return f(*args, **kwargs)

    return decorated


@chatbot.route('/token',methods=['POST'])
def generate_token():

    """
        Send Mobile Number in this API to get a token.
        eg:

        {
            "mobile_number" : 9890471562
        }
        
    """
    
    data = json.loads(request.data.decode('utf-8'))
    mobile_number = data['mobile_number']

    if "mobile_number" in data:

        # Generate a Random user id
        user_id = str(uuid.uuid4())

        session['user_details']= {"user_id":user_id,
                                  "mobile_number":mobile_number}
        
        expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)

        token = jwt.encode({'user_id':user_id, 
                            'mobile_number' : mobile_number,
                            'exp' : expiry_time},
                             chatbot.config['SECRET_KEY'])

        response =  jsonify({'token' : token.decode('UTF-8')})      
        
        return response

    else:
        
        response =  jsonify({'Error' : "Please Add Mobile Number"}), 401    
        
        return response     

@chatbot.route('/chat',methods=['POST'])
@only_token_access
def chat():

    """
        Add the Token to the client where you are sending the API request.
        
        Start the converation. Use the same format, just change the message.
        eg:

        {
            "mobile_number" : 9890471562,
            "message" : "Hi"

        }
        
    """
   

    #get data from API
    data = json.loads(request.data.decode('utf-8'))



    if data['message'].lower()=='hi':
        response = "Hi, Welcome to Route Mobile WhatsApp! We are here to resolve all your queries. Please Enter Your Name:"
        session['next_action'] = 'ask_name'

    elif session['next_action'] == 'ask_name':
        session['name'] = data['message']
        response = "Hi {Person}, Please Enter Your Email Id for reference:".format(Person=session['name'])
        session['next_action'] = 'ask_email'

    elif session['next_action'] == 'ask_email':
        response = "{Person}, Please Enter Your Residential Mailing Address:".format(Person=session['name'])
        session['next_action'] = 'ask_address'

    elif session['next_action'] == 'ask_address':
        response = "{Person},Please Enter Your Query: ".format(Person=session['name'])
        session['next_action'] = 'ask_query'

    elif session['next_action'] == 'ask_query':
        response = "Thank you {Person}, Your Query will be Resolved in next 48 hours.".format(Person=session['name'])
        session['next_action'] = None

    elif not session['next_action']:
        session.clear()
        response = "Please Enter Mobile Number,Token & Type 'Hi' to start conversation again."

    elif 'next_action' not in session:
        session.clear()
        response = "Please Enter Mobile Number,Token & Type 'Hi' to start conversation again."

    return jsonify({'response' : response}), 200


   


if __name__ == '__main__':
    chatbot.run(debug=True)    