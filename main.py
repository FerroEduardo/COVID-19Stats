import os
import csv
import datetime

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    url = "http://plataforma.saude.gov.br/novocoronavirus/"
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', str(os.path.join(Path.home(), "Downloads")))
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    driver = webdriver.Firefox(profile)

    driver.minimize_window()
    driver.get(url)
    brasilcsv = str(os.path.join(Path.home(), "Downloads/brasil.csv"))
    worldcsv = str(os.path.join(Path.home(), "Downloads/mundo.csv"))

    try:
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element((By.XPATH, '//*[@id="BRCardSuspects"]'), "%")
        )
        casos = dict()
        casos["Suspeitos"] = driver.find_element_by_xpath('//*[@id="BRCardSuspects"]').text
        casos["Confirmados"] = driver.find_element_by_xpath('//*[@id="BRCardCases"]').text
        casos["Descartados"] = driver.find_element_by_xpath('//*[@id="BRCardRefuses"]').text
        casos["Óbitos"] = driver.find_element_by_xpath('//*[@id="BRCardDeaths"]').text

        dateStr = driver.find_element_by_xpath('/html/body/div[2]/div[2]/h4/small').text
        dateStr = dateStr.split(" ")
        dia = int(dateStr[3].split("/")[0])
        mes = int(dateStr[3].split("/")[1])
        ano = int(dateStr[3].split("/")[2])
        hora = int(dateStr[5].split(":")[0])
        minuto = int(dateStr[5].split(":")[1])
        date = datetime.datetime(ano, mes, dia, hora, minuto)
        print("Dados das Unidades da Federação atualizados em " + date.strftime(
            "%d/%m/%y, %H:%M") + ". Fonte: http://plataforma.saude.gov.br/novocoronavirus/")
        if input("Deseja ver as estatísticas gerais do Brasil?(sim/nao) ") != "nao":
            for key in casos.keys():
                print(key + ": " + casos[key])
            # print(cases)
        driver.find_element_by_xpath('//*[@id="BRcsvByData"]').click()

        regioes = []
        estados = []

        with open(brasilcsv, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                if "Região" in ''.join(row["Abrangência"]):
                    regiao = dict()
                    for key in row.keys():
                        # print region stats
                        # print(key + ": " + row[key])
                        regiao[key] = row[key]
                    regioes.append(regiao)
                else:
                    estado = dict()
                    for key in row.keys():
                        # print states stats
                        # print(key + ": " + row[key])
                        estado[key] = row[key]
                    estados.append(estado)

        template = "Nome: {}, Casos suspeitos: {}({}%), Casos confirmados: {}({}%), Casos descartados: {}({}%), Óbitos: {}({}%)"
        templateCountry = "Nome: {}, Casos confirmados: {}({}%), Taxa de letalidade {}%, Óbitos: {})"
        if input("Deseja ver as estatísticas por região?(sim/nao) ") != "nao":
            for regiao in regioes:
                print(template.format(regiao["Nome"],
                                      regiao["Casos suspeitos"], regiao["% Casos suspeitos"],
                                      regiao["Casos confirmados"], regiao["% Casos confirmados"],
                                      regiao["Casos descartados"], regiao["% Casos descartados"],
                                      regiao["Óbitos"], regiao["% Óbitos"]))

        option = input("Você deseja verificar as estatísticas de estados?(sim/nao/todos) ")
        while True:
            if option.lower() == "nao":
                break

            elif option.lower() == "todos":
                for estado in estados:
                    if estado["Nome"] is not None and estado["Óbitos"] is not None:
                        print(template.format(estado["Nome"],
                                              estado["Casos suspeitos"], estado["% Casos suspeitos"],
                                              estado["Casos confirmados"], estado["% Casos confirmados"],
                                              estado["Casos descartados"], estado["% Casos descartados"],
                                              estado["Óbitos"], estado["% Óbitos"]))
                break

            else:
                name = input("Digite a sigla do estado ou o nome: ")
                try:
                    for estado in estados:
                        if len(name) <= 2:
                            if estado["Nome"] is not None and "(" + name.lower() + ")" in estado["Nome"].lower() and \
                                    estado["Óbitos"] is not None:
                                print(template.format(estado["Nome"],
                                                      estado["Casos suspeitos"], estado["% Casos suspeitos"],
                                                      estado["Casos confirmados"], estado["% Casos confirmados"],
                                                      estado["Casos descartados"], estado["% Casos descartados"],
                                                      estado["Óbitos"], estado["% Óbitos"]))
                                break

                        else:
                            if estado["Nome"] is not None and name.lower() in estado["Nome"].lower() and estado["Óbitos"] is not None:
                                print(template.format(estado["Nome"],
                                                      estado["Casos suspeitos"], estado["% Casos suspeitos"],
                                                      estado["Casos confirmados"], estado["% Casos confirmados"],
                                                      estado["Casos descartados"], estado["% Casos descartados"],
                                                      estado["Óbitos"], estado["% Óbitos"]))

                finally:
                    option = input("Deseja continuar(sim/nao) ou ver estatisticas dos países(nao)? ")

        driver.find_element_by_xpath('//*[@id="WRcsvByMap"]').click()
        paises = []
        with open(worldcsv, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                # print(row)
                pais = dict()
                for key in row.keys():
                    pais[key] = row[key]
                paises.append(pais)

        # print(countries)
        option = input("Deseja verificar estatística de algum país?(sim/nao/todos) ")
        dateStr = driver.find_element_by_xpath('/html/body/div[2]/div[3]/h4/small').text
        dateStr = dateStr.split(" ")
        dia = int(dateStr[3].split("/")[0])
        mes = int(dateStr[3].split("/")[1])
        ano = int(dateStr[3].split("/")[2])
        hora = int(dateStr[5].split(":")[0])
        minuto = int(dateStr[5].split(":")[1])
        date = datetime.datetime(ano, mes, dia, hora, minuto)
        print("Países com com casos confirmados atualizados em " + date.strftime(
            "%d/%m/%y, %H:%M") + "segundo a OMS. Fonte: http://plataforma.saude.gov.br/novocoronavirus/")
        while True:
            if option.lower() == "nao":
                break

            elif option.lower() == "todos":
                for pais in paises:
                    if pais["País"] is not None and pais["Óbitos"] is not None:
                        print(templateCountry.format(pais["País"],
                                                     pais["Casos confirmados"], pais["% Casos confirmados"],
                                                     pais["Taxa de letalidade******"], pais["Óbitos"]))
                break

            else:
                name = input("Digite o nome do país:  ")
                try:
                    for pais in paises:
                        # print(country)
                        if pais["País"] is not None and name.lower() in pais["País"].lower() and pais["Óbitos"] is not None:
                            print(templateCountry.format(pais["País"],
                                                         pais["Casos confirmados"], pais["% Casos confirmados"],
                                                         pais["Taxa de letalidade******"], pais["Óbitos"]))

                finally:
                    option = input("Deseja continuar(sim) ou sair(nao)? ")

    finally:
        driver.quit()
        try:
            os.remove(brasilcsv)
            os.remove(worldcsv)
        except Exception:
            print("error deleting files")


if __name__ == '__main__':
    main()
