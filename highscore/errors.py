def response(code):
    return {'error' : str(code)}

class Error():
    USERNAME_TAKEN = 0
    TOO_MANY_REQUESTS = 1
    
