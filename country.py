class Country():
    
    def __init__(self, name):
        self.name = name
        self.teams = []
    
    def __str__(self):
        return self.name