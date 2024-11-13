from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Relatorio
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json

def calcular_slas(chamado):
    # Ajuste conforme sua lógica específica de SLA
    sla1_tempo = float(chamado.get('SLA1', 0))
    sla2_tempo = float(chamado.get('SLA2', 0))
    sla1_meta = float(chamado.get('MetaSLA1', 4))  # 4 horas para primeiro atendimento
    sla2_meta = float(chamado.get('MetaSLA2', 24)) # 24 horas para resolução
    
    return {
        'sla1_ok': sla1_tempo <= sla1_meta,
        'sla2_ok': sla2_tempo <= sla2_meta
    }

def home(request):
    try:
        relatorio = Relatorio.objects.last()
        if not relatorio:
            return redirect('adicionar_relatorio')
        
        dados = relatorio.dados
        chamados = dados.get('root', [])
        
        # Debug para ver estrutura dos dados
        print("\n=== DADOS DO PRIMEIRO CHAMADO ===")
        if chamados:
            print(json.dumps(chamados[0], indent=2))
        print("================================\n")
        
        # === Tendência de Chamados ===
        chamados_por_data = defaultdict(lambda: {'abertos': 0, 'fechados': 0})
        
        for chamado in chamados:
            # Debug para datas
            print(f"Processando chamado:")
            print(f"DataAbertura original: {chamado.get('DataAbertura')}")
            print(f"DataFechamento original: {chamado.get('DataFechamento')}")
            
            # Tenta diferentes formatos de data possíveis
            data_abertura = None
            data_fechamento = None
            
            # Tenta obter DataAbertura
            if 'DataAbertura' in chamado:
                data_abertura = chamado['DataAbertura'].split('T')[0] if 'T' in chamado['DataAbertura'] else chamado['DataAbertura'].split(' ')[0]
            elif 'dataAbertura' in chamado:
                data_abertura = chamado['dataAbertura'].split('T')[0] if 'T' in chamado['dataAbertura'] else chamado['dataAbertura'].split(' ')[0]
            
            # Tenta obter DataFechamento
            if 'DataFechamento' in chamado:
                data_fechamento = chamado['DataFechamento'].split('T')[0] if 'T' in chamado['DataFechamento'] else chamado['DataFechamento'].split(' ')[0]
            elif 'dataFechamento' in chamado:
                data_fechamento = chamado['dataFechamento'].split('T')[0] if 'T' in chamado['dataFechamento'] else chamado['dataFechamento'].split(' ')[0]
            
            print(f"Data Abertura processada: {data_abertura}")
            print(f"Data Fechamento processada: {data_fechamento}")
            
            if data_abertura:
                chamados_por_data[data_abertura]['abertos'] += 1
            if data_fechamento:
                chamados_por_data[data_fechamento]['fechados'] += 1
        
        # Debug do resultado
        print("\n=== DADOS POR DATA ===")
        print(json.dumps(dict(chamados_por_data), indent=2))
        print("=====================\n")
        
        # Ordenar datas
        datas = sorted(chamados_por_data.keys())
        tendencia_data = {
            'datas': datas,
            'abertos': [chamados_por_data[d]['abertos'] for d in datas],
            'fechados': [chamados_por_data[d]['fechados'] for d in datas]
        }
        
        print("\n=== DADOS DE TENDÊNCIA ===")
        print(json.dumps(tendencia_data, indent=2))
        print("=========================\n")
        
        total_chamados = len(chamados)
        
        # === SLAs ===
        sla_stats = {'sla1': {'ok': 0, 'nok': 0}, 'sla2': {'ok': 0, 'nok': 0}}
        for chamado in chamados:
            slas = calcular_slas(chamado)
            if slas['sla1_ok']:
                sla_stats['sla1']['ok'] += 1
            else:
                sla_stats['sla1']['nok'] += 1
            if slas['sla2_ok']:
                sla_stats['sla2']['ok'] += 1
            else:
                sla_stats['sla2']['nok'] += 1
        
        sla_percentuais = {
            'sla1': {
                'ok': (sla_stats['sla1']['ok'] / total_chamados * 100) if total_chamados > 0 else 0,
                'nok': (sla_stats['sla1']['nok'] / total_chamados * 100) if total_chamados > 0 else 0
            },
            'sla2': {
                'ok': (sla_stats['sla2']['ok'] / total_chamados * 100) if total_chamados > 0 else 0,
                'nok': (sla_stats['sla2']['nok'] / total_chamados * 100) if total_chamados > 0 else 0
            }
        }

        # === Prioridades ===
        prioridade_count = Counter(c.get('Prioridade', 'Não definida') for c in chamados)

        # === Tempo Médio de Resolução ===
        tempos_resolucao = defaultdict(list)
        for chamado in chamados:
            data = chamado.get('DataFechamento', '').split('T')[0]
            tempo = float(chamado.get('TempoResolucao', 0))
            if data and tempo:
                tempos_resolucao[data].append(tempo)
        
        tempo_medio_por_dia = {
            data: sum(tempos)/len(tempos) 
            for data, tempos in tempos_resolucao.items()
        }

        # === Atendimentos por Operador ===
        operador_count = Counter(c.get('Operador', 'Não atribuído') for c in chamados)
        
        # Ordenar por quantidade de atendimentos
        operadores_ordenados = sorted(
            operador_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]  # Top 10 operadores

        # === Tipos de Chamados ===
        tipo_count = Counter(c.get('Assunto', 'Não definido') for c in chamados)
        tipos_ordenados = sorted(
            tipo_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]  # Top 10 tipos

        contexto = {
            'sla_percentuais': sla_percentuais,
            'prioridade_labels': list(prioridade_count.keys()),
            'prioridade_data': list(prioridade_count.values()),
            'tempo_medio_por_dia': tempo_medio_por_dia,
            'operador_labels': [op[0] for op in operadores_ordenados],
            'operador_data': [op[1] for op in operadores_ordenados],
            'tendencia_data': tendencia_data,
            'tipo_labels': [tipo[0] for tipo in tipos_ordenados],
            'tipo_data': [tipo[1] for tipo in tipos_ordenados],
            'total_chamados': total_chamados,
            'ultima_atualizacao': relatorio.data_importacao
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
