from django.db import models
import json

class Relatorio(models.Model):
    chave = models.CharField(max_length=100, unique=True)
    data_importacao = models.DateTimeField(auto_now_add=True)
    dados = models.JSONField()

    def save(self, *args, **kwargs):
        # Garante que dados seja sempre um objeto Python válido
        if isinstance(self.dados, str):
            try:
                self.dados = json.loads(self.dados)
            except json.JSONDecodeError:
                pass  # Mantém como string se não for JSON válido
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Relatório {self.chave} - {self.data_importacao}"
