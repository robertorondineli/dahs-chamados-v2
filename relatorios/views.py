from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Relatorio
from .utils import processar_dados_graficos
import json
from datetime import datetime

@cache_page(60 * 15)  # Cache por 15 minutos
def home(request):
    try:
        relatorio = Relatorio.objects.last()
        if not relatorio:
            return redirect('adicionar_relatorio')
        
        dados = relatorio.dados
        chamados = dados.get('root', [])
        dados_processados = processar_dados_graficos(chamados)
        
        return render(request, 'relatorios/dashboard.html', dados_processados)
    except Exception as e:
        print(f"Erro ao processar dashboard: {str(e)}")
        return render(request, 'relatorios/error.html', {'error': str(e)})

def adicionar_relatorio(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.POST.get('dados', '{}'))
            relatorio = Relatorio.objects.create(
                chave=f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                dados=dados
            )
            messages.success(request, 'Relatório adicionado com sucesso!')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Erro ao adicionar relatório: {str(e)}')
    
    return render(request, 'relatorios/adicionar.html')

def lista_relatorios(request):
    try:
        relatorios = Relatorio.objects.all().order_by('-data_importacao')
        return render(request, 'relatorios/lista.html', {'relatorios': relatorios})
    except Exception as e:
        messages.error(request, f'Erro ao listar relatórios: {str(e)}')
        return redirect('home')

def excluir_relatorio(request, pk):
    relatorio = get_object_or_404(Relatorio, pk=pk)
    if request.method == 'POST':
        relatorio.delete()
        messages.success(request, 'Relatório excluído com sucesso!')
        return redirect('lista_relatorios')
    return render(request, 'relatorios/excluir.html', {'relatorio': relatorio})

def dashboard(request, relatorio_id):
    relatorio = get_object_or_404(Relatorio, id=relatorio_id)
    
    # Processando dados para os gráficos
    dados = relatorio.dados
    
    # Exemplo de processamento (ajuste conforme a estrutura real dos seus dados)
    status_count = Counter(item.get('status') for item in dados)
    categoria_count = Counter(item.get('categoria') for item in dados)
    
    contexto = {
        'relatorio': relatorio,
        'status_labels': list(status_count.keys()),
        'status_data': list(status_count.values()),
        'categoria_labels': list(categoria_count.keys()),
        'categoria_data': list(categoria_count.values()),
    }
    
    return render(request, 'relatorios/dashboard.html', contexto)
