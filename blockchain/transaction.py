

# replacing 'data' filler with 'transactions'
class Transaction():
    # basic stuff for now
    def __init__(self, sender_address, recip_address, amount):
        self.sender_address = sender_address
        self.recip_address = recip_address
        self.amount = amount