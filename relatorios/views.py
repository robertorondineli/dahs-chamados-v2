from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Relatorio
from .services import DeskAPI
from django.http import JsonResponse
from django.db.models import Count
from collections import Counter
import json
from datetime import datetime

def home(request):
    try:
        relatorio = Relatorio.objects.last()
        if not relatorio:
            return redirect('adicionar_relatorio')
        
        # Converte os dados para objeto Python
        try:
            if isinstance(relatorio.dados, str):
                dados = json.loads(relatorio.dados)
            else:
                dados = relatorio.dados
                
            # Debug para ver a estrutura dos dados
            print("Estrutura dos dados:", dados.keys() if isinstance(dados, dict) else type(dados))
            
            # Processando dados para os gráficos
            status_count = Counter()
            categoria_count = Counter()
            prioridade_count = Counter()
            datas = set()
            
            # Assumindo que os dados estão em uma chave 'items' ou similar
            items = dados.get('items', []) if isinstance(dados, dict) else dados
            
            if not items:
                print("Dados recebidos:", dados)
                return render(request, 'relatorios/error.html', {
                    'error': 'Formato de dados inválido'
                })
            
            for item in items:
                if isinstance(item, str):
                    item = json.loads(item)
                
                # Ajuste esses campos conforme a estrutura real dos seus dados
                status = str(item.get('status', 'Não definido'))
                categoria = str(item.get('categoria', 'Não definida'))
                prioridade = str(item.get('prioridade', 'Não definida'))
                data = str(item.get('data', '')).split('T')[0]
                
                status_count[status] += 1
                categoria_count[categoria] += 1
                prioridade_count[prioridade] += 1
                if data:
                    datas.add(data)
            
            datas_disponiveis = sorted(list(datas)) if datas else []
            data_selecionada = request.GET.get('data', datas_disponiveis[-1] if datas_disponiveis else None)
            
            contexto = {
                'relatorio': relatorio,
                'datas_disponiveis': datas_disponiveis,
                'data_selecionada': data_selecionada,
                'status_labels': list(status_count.keys()),
                'status_data': list(status_count.values()),
                'categoria_labels': list(categoria_count.keys()),
                'categoria_data': list(categoria_count.values()),
                'prioridade_labels': list(prioridade_count.keys()),
                'prioridade_data': list(prioridade_count.values()),
                'total_chamados': len(items)
            }
            
            return render(request, 'relatorios/dashboard.html', contexto)
            
        except json.JSONDecodeError as e:
            print("Erro ao decodificar JSON:", str(e))
            print("Dados recebidos:", relatorio.dados)
            return render(request, 'relatorios/error.html', {
                'error': 'Erro ao processar dados do relatório'
            })
            
    except Exception as e:
        print("Erro geral:", str(e))
        return render(request, 'relatorios/error.html', {
            'error': 'Erro ao carregar dashboard'
        })

def adicionar_relatorio(request):
    if request.method == 'POST':
        chave = request.POST.get('chave')
        if not chave:
            messages.error(request, 'Por favor, forneça uma chave de relatório')
            return render(request, 'relatorios/adicionar.html')
        
        api = DeskAPI()
        if not api.autenticar():
            messages.error(request, 'Falha na autenticação com a API')
            return render(request, 'relatorios/adicionar.html')
        
        print(f"Token obtido: {api.token}")  # Debug
        
        dados = api.obter_relatorio(chave)
        if dados:
            try:
                Relatorio.objects.create(
                    chave=chave,
                    dados=dados
                )
                messages.success(request, 'Relatório importado com sucesso!')
                return redirect('home')  # Alterado para 'home' já que 'lista_relatorios' ainda não existe
            except Exception as e:
                messages.error(request, f'Erro ao salvar relatório: {str(e)}')
        else:
            messages.error(request, 'Não foi possível obter os dados do relatório')
    
    return render(request, 'relatorios/adicionar.html')

def lista_relatorios(request):
    relatorios = Relatorio.objects.all().order_by('-data_importacao')
    return render(request, 'relatorios/lista.html', {'relatorios': relatorios})

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
