def tryExceptNone(func):
    def __func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None
    
    return __func

def tryExceptFalse(func):
    def __func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return False 
    
    return __func
