import json, sys, g4f

g4f.version_check = False

AvailableProviders = json.loads(sys.argv[1])

try:
    Query = json.loads(sys.argv[2])
except:
    Query = {}

def FormatQueryMessages(Messages: tuple) -> tuple:
    BASE_MESSAGES = [{
        'role': 'system',
        'content': 'voce é um atendente virtual de uma grande empresa de planos de saúde chamada Digital Saúde, voce comercializa planos de diversas operadoras. sua missão é coletar o nome, telefone e email do cliente para futuramente um consultor especializado entrar em contato para realizar a cotação. Você não faz parte do suporte e atendimento de nenhuma das operadoras, só comercializa elas, mas so informe essa informação caso o cliente vier atras disso.'
    }]
    return BASE_MESSAGES + [ { 
        'role': Message.get('Role', 'user').lower(), 
        'content': Message.get('Content') } for Message in Messages ] 

def GetProviderData(Provider) -> dict:
    ImportedProvider = ImportProvider(Provider)
    if(ImportedProvider is None):
        return {
            'Name': 'Automatic',
            'Website': 'https://github.com/codewithrodi/Lovelace/',
            'Models': ['gpt-3.5-turbo', 'gpt-4']
        }
    Models = []
    if(ImportedProvider.supports_gpt_35_turbo):
        Models.append('gpt-3.5-turbo')
    if(ImportedProvider.supports_gpt_4):
        Models.append('gpt-4')
    return {
        'Name': Provider,
        'Website': ImportedProvider.url,
        'Models': Models
    }

def ImportProvider(ProviderName: str): 
    if(ProviderName == 'Automatic'):
        return None
    return eval('g4f.Provider.' + ProviderName)

def MainFN() -> None:
    try:
        if sys.argv[3] == 'PROVIDERS':
            print(json.dumps({
                'Providers': {
                    'WS': [GetProviderData(Provider) for Provider in AvailableProviders['WS']],
                    'API': [GetProviderData(Provider) for Provider in AvailableProviders['API']]
                }
            }))
        elif sys.argv[3] == 'API' or sys.argv[3] == 'WS':
            Model = Query['Model']
            Provider = None if Query['Provider'] == 'Automatic' else ImportProvider(Query['Provider'])
            Messages = FormatQueryMessages(Query['Messages'])
            if sys.argv[3] == 'API':
                Response = g4f.ChatCompletion.create(
                    model=Model,
                    provider=Provider, 
                    messages=Messages)
                print(Response.join('\n'))
            else:
                StreamedResponse = g4f.ChatCompletion.create(
                    model=Model,
                    messages=Messages,
                    provider=Provider, 
                    stream=True)
                for Message in StreamedResponse:
                    print(Message, end='', flush=True)
    except Exception as GPTException:
        print(GPTException)

if __name__ == '__main__':
    MainFN()
