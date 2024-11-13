from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Relatorio
from collections import Counter, defaultdict
from datetime import datetime
import json

def calcular_sla(chamado):
    # Ajuste conforme sua lógica de SLA
    tempo_resolucao = chamado.get('TempoResolucao', 0)
    sla_esperado = chamado.get('SLAEsperado', 24)  # 24 horas como padrão
    return tempo_resolucao <= sla_esperado

def home(request):
    try:
        relatorio = Relatorio.objects.last()
        if not relatorio:
            return redirect('adicionar_relatorio')
        
        dados = relatorio.dados
        chamados = dados.get('root', [])
        
        # === SLA ===
        total_chamados = len(chamados)
        chamados_no_sla = sum(1 for c in chamados if calcular_sla(c))
        sla_data = {
            'dentro': (chamados_no_sla / total_chamados * 100) if total_chamados > 0 else 0,
            'fora': ((total_chamados - chamados_no_sla) / total_chamados * 100) if total_chamados > 0 else 0
        }

        # === Prioridades ===
        prioridade_count = Counter(c.get('Prioridade', 'Não definida') for c in chamados)

        # === Tempo Médio de Resolução ===
        tempos_resolucao = [float(c.get('TempoResolucao', 0)) for c in chamados if c.get('TempoResolucao')]
        tempo_medio = sum(tempos_resolucao) / len(tempos_resolucao) if tempos_resolucao else 0

        # === Produtividade por Operador ===
        operador_count = Counter(c.get('Operador', 'Não atribuído') for c in chamados)

        # === Tendência de Chamados ===
        chamados_por_data = defaultdict(lambda: {'abertos': 0, 'fechados': 0})
        for chamado in chamados:
            data_abertura = chamado.get('DataAbertura', '').split('T')[0]
            data_fechamento = chamado.get('DataFechamento', '').split('T')[0]
            
            if data_abertura:
                chamados_por_data[data_abertura]['abertos'] += 1
            if data_fechamento:
                chamados_por_data[data_fechamento]['fechados'] += 1

        # Ordenar datas
        datas = sorted(chamados_por_data.keys())
        tendencia_data = {
            'datas': datas,
            'abertos': [chamados_por_data[d]['abertos'] for d in datas],
            'fechados': [chamados_por_data[d]['fechados'] for d in datas]
        }

        # === Categorias ===
        categoria_count = Counter(c.get('Categoria', 'Não definida') for c in chamados)

        contexto = {
            'sla_data': sla_data,
            'prioridade_labels': list(prioridade_count.keys()),
            'prioridade_data': list(prioridade_count.values()),
            'tempo_medio_resolucao': round(tempo_medio, 2),
            'operador_labels': list(operador_count.keys()),
            'operador_data': list(operador_count.values()),
            'tendencia_data': tendencia_data,
            'categoria_labels': list(categoria_count.keys()),
            'categoria_data': list(categoria_count.values()),
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
