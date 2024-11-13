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
        
        dados = relatorio.dados
        
        # Os chamados estão dentro da chave 'root'
        if isinstance(dados, dict) and 'root' in dados:
            items = dados['root']
            
            print("\n=== DADOS DO RELATÓRIO ===")
            print("Total de chamados:", len(items))
            if items:
                print("Exemplo do primeiro chamado:", items[0])
            print("==========================\n")
            
            status_count = Counter()
            categoria_count = Counter()
            prioridade_count = Counter()
            datas = set()
            
            for item in items:
                # Ajustando para as chaves corretas do seu JSON
                status = str(item.get('Status', 'Não definido'))
                categoria = str(item.get('Categoria', 'Não definida'))
                prioridade = str(item.get('Prioridade', 'Não definida'))
                data = str(item.get('DataAbertura', '')).split('T')[0] if item.get('DataAbertura') else ''
                
                status_count[status] += 1
                categoria_count[categoria] += 1
                prioridade_count[prioridade] += 1
                if data:
                    datas.add(data)
            
            datas_disponiveis = sorted(list(datas)) if datas else []
            data_selecionada = request.GET.get('data', datas_disponiveis[-1] if datas_disponiveis else None)
            
            # Adiciona informações do relatório ao contexto
            contexto = {
                'relatorio': relatorio,
                'nome_relatorio': dados.get('NomeRelatorio', 'Relatório de Chamados'),
                'total_registros': dados.get('total', 0),
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
        else:
            return render(request, 'relatorios/error.html', {
                'error': f'Nenhum chamado encontrado no relatório. Estrutura dos dados: {dados.keys() if isinstance(dados, dict) else type(dados)}'
            })
        
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
