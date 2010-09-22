


class Payment(orm.CreatedAtAbstractBase):
    #convenient boolean
    transaction = models.OneToOneField(Transaction, blank=True, null=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    #ogone information feedback
    status_category = models.CharField(max_length=255, blank=True, null=True)
    acceptance = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    brand = models.CharField(max_length=255, blank=True, null=True)
    cardno = models.CharField(max_length=255, blank=True, null=True)
    cccty = models.CharField(max_length=255, blank=True, null=True)
    currency = models.CharField(max_length=255, blank=True, null=True)
    cvccheck = models.CharField(max_length=255, blank=True, null=True)
    eci = models.CharField(max_length=255, blank=True, null=True)
    ed = models.CharField(max_length=255, blank=True, null=True)
    ip = models.CharField(max_length=255, blank=True, null=True)
    ipcty = models.CharField(max_length=255, blank=True, null=True)
    ncerror = models.CharField(max_length=255, blank=True, null=True)
    payid = models.CharField(max_length=255, blank=True, null=True)
    pm = models.CharField(max_length=255, blank=True, null=True)
    shasign = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    trxdate = models.DateField(blank=True, null=True)
    vc = models.CharField(max_length=255, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        '''
        Sets the completed flag if required
        '''
        import datetime
        if self.status_category == 'accepted' and not self.completed:
            self.completed = True
            self.completed_at = datetime.datetime.today()
        return orm.CreatedAtAbstractBase.save(self, *args, **kwargs)