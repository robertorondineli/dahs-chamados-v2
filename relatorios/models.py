from django.db import models

class Relatorio(models.Model):
    chave = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True,
        help_text="Identificador único do relatório"
    )
    dados = models.JSONField(
        help_text="Dados dos chamados em formato JSON"
    )
    data_importacao = models.DateTimeField(
        auto_now_add=True, 
        db_index=True,
        help_text="Data e hora da importação"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['data_importacao']),
            models.Index(fields=['chave', 'data_importacao']),
        ]
        ordering = ['-data_importacao']
        verbose_name = 'Relatório'
        verbose_name_plural = 'Relatórios'

    def __str__(self):
        return f"Relatório {self.chave} - {self.data_importacao}"

    def get_chamados_count(self):
        """Retorna o número de chamados de forma eficiente"""
        if self.dados and 'root' in self.dados:
            return len(self.dados.get('root', []))
        return 0
