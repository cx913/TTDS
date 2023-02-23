from django.db import models

# Create your models here.

class Recipe(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
'''
class Token(models.Model):
    token = models.CharField(max_length=255)
    def __str__(self):
        return self.token

class Document(models.Model):
    doc_id = models.CharField(max_length=255)
    tokens = models.ManyToManyField(Token, through='TokenValue')
    def __str__(self):
        return self.doc_id

class TokenValue(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    value = models.IntegerField()
    def __str__(self):
        return (self.token, self.document, self.value)
'''

class TokenData(models.Model):
    token = models.CharField(max_length=255)
    doc_id = models.CharField(max_length=255)
    data = models.CharField(max_length=255)