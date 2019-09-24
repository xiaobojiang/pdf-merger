class general_response:

    def __init__ (self,success=True,payload=""):
        self.success = success 
        self.payload = payload

    def set_success(self,success):
        self.success = success 

    def get_success(self):
        return self.success

    def set_payload(self,payload):
        self.payload = payload

    def get_payload(self):
        return self.payload