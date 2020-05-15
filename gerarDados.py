import os
import csv
import shutil
import requests
import datetime
import dateutil
import traceback


def obterUFEstadoPorNome(estado):
    """
    Retorna o codigo UF do estado a partir do nome do estado
    :param estado: Nome do estado
    :return codigoDoEstado: Código UF do estado
    """
    try:
        with open("./recursos/estados.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for state in reader:
                if state["Unidade_Federativa"].lower() == estado.strip().lower():
                    return state["UF"]
    except Exception as exc:
        print("[ERROR]{0}".format(exc))


def obterNomeEstadoPorUF(uf):
    """
    Retorna o nome do estado a partir da sigla do estado
    :param uf: Código UF do estado
    :return nomeDoEstado: Nome do estado
    """
    with open("./recursos/estados.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for state in reader:
            if state["UF"].lower() == uf.lower():
                return state["Unidade_Federativa"]


def obterPrimeiroNomeEstadoPorEntrada(entrada):
    """
    Retorna o nome do estado a partir da sigla do estado
    :param uf: Código UF do estado
    :return nomeDoEstado: Nome do estado
    """
    with open("./recursos/estados.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for state in reader:
            if entrada.lower() in state["Unidade_Federativa"].lower():
                return state["Unidade_Federativa"]


def main():
    url = "https://covid.saude.gov.br/"
    pastaAtual = os.getcwd()
    try:
        application_id_request = 'unAFkcaNDeXajurGB7LChj8SgQYS2ptm'

        # Captura dados gerais da página
        print("[LOG]Capturando dados gerais.")
        dados_gerais = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalSintese',
                                    headers={"X-Parse-Application-Id": application_id_request}).json()
        casos = dict()
        casos["Confirmados"] = int(dados_gerais[0]['casosAcumuladoN'])
        casos["Obitos"] = int(dados_gerais[0]['obitosAcumuladoN'])
        casos["Letalidade(%)"] = float((casos["Obitos"] * 100) / casos["Confirmados"])
        # Pega hora em UTC e converte
        utc_zone = dateutil.tz.tzutc()
        local_zone = dateutil.tz.tzlocal()
        utc = datetime.datetime.strptime(dados_gerais[0]['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        utc = utc.replace(tzinfo=utc_zone)
        # Converte para zona local
        hora_local_obj = utc.astimezone(local_zone)
        hora = hora_local_obj.hour
        minuto = hora_local_obj.minute
        dia = hora_local_obj.day
        mes = hora_local_obj.month
        ano = hora_local_obj.year
        date = datetime.datetime(ano, mes, dia, hora, minuto)
        print("[LOG]Dados gerais extraídos.")
        print("Dados atualizados " + date.strftime("%d/%m/%Y %H:%M") + ". Fonte: " + url)

        regioes = []
        print("[LOG]Dados das regiões sendo extraídos.")
        dados_regioes = dados_gerais

        for i in range(1, 6):
            dado = dict()
            dado['Nome'] = dados_regioes[i]['_id']
            dado['Casos'] = int(dados_regioes[i]['casosAcumulado'])
            dado['PorcentagemDeCasosRelacional'] = (dado['Casos'] / casos["Confirmados"]) * 100
            regioes.append(dado)
        print("[LOG]Dados das regiões extraídos.")

        estados = []
        # Captura dados dos estados
        print("[LOG]Dados dos estados sendo extraídos.")
        # dados_estados = dados_regioes
        for regiao in dados_regioes[1:6]:
            for estado in regiao['listaMunicipios']:
                dado = dict()
                dado['Nome'] = obterNomeEstadoPorUF(estado['_id'])
                dado['Casos'] = int(estado['casosAcumulado'])
                dado['PorcentagemDeCasosRelacional'] = float((dado['Casos'] / casos["Confirmados"]) * 100.0)
                dado['Obitos'] = int(estado['obitosAcumulado'])
                dado['Letalidade'] = float((dado['Obitos'] * 100) / dado['Casos'])
                estados.append(dado)
        print("[LOG]Dados dos estados extraídos.")

        with open("./dados/" + date.strftime("%d-%m-%Y--%H-%M") + ".csv", "w", newline="",
                  encoding="utf-8") as file:
            field_names = ["Nome", "Casos", "PorcentagemDeCasosRelacional", "Obitos", "Letalidade", "Atualizado"]
            writer = csv.DictWriter(file,
                                    fieldnames=field_names,
                                    delimiter=";",
                                    quotechar='"',
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            for regiao in regioes:
                writer.writerow({"Nome": regiao["Nome"],
                                 "Casos": regiao["Casos"],
                                 "PorcentagemDeCasosRelacional": regiao["PorcentagemDeCasosRelacional"],
                                 "Obitos": "",
                                 "Letalidade": "",
                                 "Atualizado": ""
                                 })
            for estado in estados:
                nome = estado["Nome"] + "(" + obterUFEstadoPorNome(estado["Nome"]) + ")"
                writer.writerow({"Nome": nome,
                                 "Casos": estado["Casos"],
                                 "PorcentagemDeCasosRelacional": "{:.5f}".format(
                                     estado["PorcentagemDeCasosRelacional"]),
                                 "Obitos": estado["Obitos"],
                                 "Letalidade": estado["Letalidade"],
                                 "Atualizado": ""
                                 })
            # writer.writerows(estados)
            writer.writerow({"Nome": "Total",
                             "Casos": str(casos["Confirmados"]).replace(".", ""),
                             "PorcentagemDeCasosRelacional": "100",
                             "Obitos": casos["Obitos"],
                             "Letalidade": casos["Letalidade(%)"],
                             "Atualizado": date.strftime("%d-%m-%Y--%H-%M")
                             })

        shutil.copyfile("./dados/" + date.strftime("%d-%m-%Y--%H-%M") + ".csv", "dados/maisRecente.csv")

        print(
            date.strftime("%d-%m-%Y--%H-%M") + ".csv criado na pasta dados, que se encontra na pasta desse script.")
        print("maisRecente.csv foi atualizado.")

        dados_acumulados = []

        req = requests.get("https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalCasos")
        req_json = req.json()
        for dado in req_json['dias']:
            dados_acumulados.append({"Data": dado["_id"],
                                    "Confirmados": dado["casosAcumulado"],
                                    "Obitos": dado["obitosAcumulado"]
                                    })
        with open("dados/casosAcumulados.csv", "w", newline="", encoding="utf-8") as file:
            field_names = ["Data", "Confirmados", "Novos Confirmados", "Obitos", "Novos Obitos"]
            writer = csv.DictWriter(file,
                                    fieldnames=field_names,
                                    delimiter=";",
                                    quotechar='"',
                                    quoting=csv.QUOTE_NONNUMERIC
                                    )
            writer.writeheader()
            numero_obitos_anterior = None
            numero_de_casos_anterior = None
            for dado in dados_acumulados:
                if numero_de_casos_anterior == None and numero_obitos_anterior == None:
                    numero_de_casos_anterior = dado["Confirmados"]
                    numero_obitos_anterior = dado["Obitos"]
                    writer.writerow({"Data": dado["Data"],
                                     "Confirmados": dado["Confirmados"],
                                     "Novos Confirmados": "0",
                                     "Obitos": dado["Obitos"],
                                     "Novos Obitos": "0"
                                     })
                else:
                    writer.writerow({"Data": dado["Data"],
                                     "Confirmados": dado["Confirmados"],
                                     "Novos Confirmados": int(dado["Confirmados"]) - int(numero_de_casos_anterior),
                                     "Obitos": dado["Obitos"],
                                     "Novos Obitos": int(dado["Obitos"]) - int(numero_obitos_anterior)
                                     })
                    numero_de_casos_anterior = dado["Confirmados"]
                    numero_obitos_anterior = dado["Obitos"]

        casos_estaduais = dict()
        print("[LOG]Obtendo casos detalhados dos estados")

        # DICIONARIO DE ESTADOS
        # CADA ESTADO TEM UMA LISTA
        # CADA LISTA POSSUI OUTRAS 5 LISTAS:
        # data
        # casosNovos
        # casosAcumulados
        # obitosNovos
        # obitosAcumulado

        casos_detalhados_estados = requests.get(
            'https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalRegiaoUf').json()

        for regiao in regioes:
            nome_regiao = regiao['Nome']
            for estado in casos_detalhados_estados[nome_regiao]:
                dia_anterior = dict()
                for dia in casos_detalhados_estados[nome_regiao][estado]['dias']:
                    if estado not in casos_estaduais:
                        casos_estaduais[estado] = []
                        casos_estaduais[estado].append([dia['_id']])
                        casos_estaduais[estado].append([dia['casosAcumulado']])  # casos novos
                        casos_estaduais[estado].append([dia['casosAcumulado']])  # casos acumulados
                        casos_estaduais[estado].append([dia['obitosAcumulado']])  # obitos novos
                        casos_estaduais[estado].append([dia['obitosAcumulado']])  # obitos acumulados
                        casos_estaduais[estado].append(regiao)  # obitos acumulados
                        dia_anterior['casos'] = dia['casosAcumulado']
                        dia_anterior['obitos'] = dia['obitosAcumulado']
                    else:
                        casos_estaduais[estado][0].append(dia['_id'])
                        casos_estaduais[estado][1].append(dia['casosAcumulado'] - dia_anterior['casos'])  # casos novos
                        casos_estaduais[estado][2].append(dia['casosAcumulado'])  # casos acumulados
                        casos_estaduais[estado][3].append(
                            dia['obitosAcumulado'] - dia_anterior['obitos'])  # obitos novos
                        casos_estaduais[estado][4].append(dia['obitosAcumulado'])  # obitos acumulados
                        dia_anterior['casos'] = dia['casosAcumulado']
                        dia_anterior['obitos'] = dia['obitosAcumulado']

    # except Exception as exc:
    #     print("[ERROR]{0}".format(exc))

    finally:
        print("[LOG]Encerrando script.")
        print("[LOG]Script encerrado.")
        print("Todos os dados foram extraídos de: " + url + ".")


if __name__ == '__main__':
    main()
