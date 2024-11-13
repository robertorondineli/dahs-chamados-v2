from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Relatorio
from collections import Counter
from .services import DeskAPI
import json

def home(request):
    try:
        relatorio = Relatorio.objects.last()
        if not relatorio:
            return redirect('adicionar_relatorio')
        
        # Debug - Mostrar estrutura dos dados
        print("=== DADOS DO RELATÓRIO ===")
        print(type(relatorio.dados))
        print(relatorio.dados)
        print("==========================")
        
        dados = relatorio.dados
        
        # Assumindo que os dados estão em uma lista de chamados
        if isinstance(dados, list):
            items = dados
        elif isinstance(dados, dict):
            # Se for um dicionário, procura por uma chave que contenha os chamados
            items = dados.get('Chamados') or dados.get('chamados') or dados.get('items') or []
        else:
            items = []
        
        if not items:
            print("Nenhum item encontrado nos dados")
            return render(request, 'relatorios/error.html', {
                'error': f'Nenhum chamado encontrado no relatório. Estrutura: {type(dados)}'
            })
        
        # Debug - Mostrar primeiro item
        print("=== PRIMEIRO ITEM ===")
        print(items[0] if items else "Sem items")
        print("====================")
        
        status_count = Counter()
        categoria_count = Counter()
        prioridade_count = Counter()
        datas = set()
        
        for item in items:
            # Tenta diferentes chaves possíveis para cada campo
            status = (
                item.get('Status') or 
                item.get('status') or 
                item.get('StatusChamado') or 
                'Não definido'
            )
            
            categoria = (
                item.get('Categoria') or 
                item.get('categoria') or 
                item.get('CategoriaChamado') or 
                'Não definida'
            )
            
            prioridade = (
                item.get('Prioridade') or 
                item.get('prioridade') or 
                item.get('PrioridadeChamado') or 
                'Não definida'
            )
            
            data = (
                item.get('DataAbertura') or 
                item.get('dataAbertura') or 
                item.get('Data') or 
                ''
            )
            
            if isinstance(data, str) and data:
                data = data.split('T')[0] if 'T' in data else data.split(' ')[0]
            
            status_count[str(status)] += 1
            categoria_count[str(categoria)] += 1
            prioridade_count[str(prioridade)] += 1
            if data:
                datas.add(str(data))
        
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
        
    except Exception as e:
        print(f"Erro ao processar dashboard: {str(e)}")
        return render(request, 'relatorios/error.html', {
            'error': f'Erro ao processar dashboard: {str(e)}'
        })

def adicionar_relatorio(request):
    if request.method == 'POST':
        chave = request.POST.get('chave')
        if not chave:
            messages.error(request, 'Por favor, forneça uma chave de relatório')
            return render(request, 'relatorios/adicionar.html')
        
        try:
            # Verifica se já existe um relatório com esta chave
            relatorio_existente = Relatorio.objects.filter(chave=chave).first()
            
            api = DeskAPI()
            if not api.autenticar():
                messages.error(request, 'Falha na autenticação com a API')
                return render(request, 'relatorios/adicionar.html')
            
            dados = api.obter_relatorio(chave)
            
            if dados:
                try:
                    if relatorio_existente:
                        print(f"Atualizando relatório existente com chave: {chave}")
                        relatorio_existente.dados = dados
                        relatorio_existente.save()
                        messages.success(request, f'Relatório {chave} atualizado com sucesso!')
                    else:
                        print(f"Criando novo relatório com chave: {chave}")
                        Relatorio.objects.create(
                            chave=chave,
                            dados=dados
                        )
                        messages.success(request, f'Novo relatório {chave} importado com sucesso!')
                    
                    return redirect('home')
                except Exception as e:
                    print(f"Erro ao salvar/atualizar relatório: {str(e)}")
                    messages.error(request, f'Erro ao processar relatório: {str(e)}')
            else:
                messages.error(request, 'Não foi possível obter os dados do relatório')
        except Exception as e:
            print(f"Erro na importação: {str(e)}")
            messages.error(request, f'Erro ao processar relatório: {str(e)}')
    
    # Busca relatórios existentes para mostrar na página
    relatorios = Relatorio.objects.all().order_by('-data_importacao')
    return render(request, 'relatorios/adicionar.html', {'relatorios': relatorios})

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
