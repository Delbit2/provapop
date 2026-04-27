from app import app, db, Questao

def popular_banco():
    with app.app_context():
        # Verificando se já existem questões para não duplicar
        if Questao.query.count() > 0:
            print("⚠️ O banco já possui questões. Abortando para evitar duplicações.")
            return

        questoes_data = [
            {
                'titulo_musica': 'Toda Forma de Poder',
                'artista': 'Engenheiros do Hawaii',
                'letra': '"E toda forma de poder\nMe inspira terror\nMe inspira horror\nDeixa eu te dizer\nPor que eu sou contra\nA toda forma de poder"',
                'enunciado': 'Na letra da canção "Toda Forma de Poder", dos Engenheiros do Hawaii, o compositor expressa uma crítica social. Considerando o contexto histórico e social do Brasil na década de 1980, a mensagem central da música refere-se à crítica:',
                'alternativa_correta': 'C',
                'alternativa_a': 'à política partidária e aos sistemas eleitorais democráticos, defendendo uma monarquia absoluta.',
                'alternativa_b': 'à concentração de poder nas mãos de grupos minoritários, sem questionar as estruturas sociais existentes.',
                'alternativa_c': 'às estruturas autoritárias e à concentração de poder que limitavam as liberdades individuais e coletivas.',
                'alternativa_d': 'exclusivamente ao poder militar, ignorando outros aspectos do contexto social e político da época.',
                'alternativa_e': 'ao poder econômico, sem relacionar com as questões políticas e sociais do período.',
                'categoria': 'Outros',
                'disciplina': 'História',
                'habilidade_enem': 'H15'
            },
            {
                'titulo_musica': 'Cálice',
                'artista': 'Chico Buarque e Gilberto Gil',
                'letra': '"Como beber dessa bebida amarga / Tragar a dor, engolir a labuta / Mesmo calada a boca, resta o peito / Silêncio na cidade não se escuta / De que me vale ser filho da santa / Melhor seria ser filho da outra / Outra realidade menos morta / Tanta mentira, tanta força bruta"',
                'enunciado': 'A música "Cálice" utiliza um jogo sonoro entre a palavra "cálice" e a expressão imperativa "cale-se". Lançada em 1978, a letra faz referência direta a qual característica marcante do período em que foi composta?',
                'alternativa_correta': 'A',
                'alternativa_a': 'À censura institucionalizada imposta pelo Regime Militar aos meios de comunicação e à produção artística.',
                'alternativa_b': 'À imposição de dogmas religiosos pelo clero católico durante a transição democrática.',
                'alternativa_c': 'À proibição do consumo de bebidas alcoólicas implementada por decretos de moralidade pública.',
                'alternativa_d': 'Ao silêncio das classes trabalhadoras rurais que migravam em massa para os centros urbanos.',
                'alternativa_e': 'À falta de liberdade de escolha de consumo em um mercado fechado à importação de produtos culturais.',
                'categoria': 'Enem',
                'disciplina': 'Literatura',
                'habilidade_enem': 'H15'
            },
            {
                'titulo_musica': 'Construção',
                'artista': 'Chico Buarque',
                'letra': '"Amou daquela vez como se fosse a última / Beijou sua mulher como se fosse a última / E cada filho seu como se fosse o único / E atravessou a rua com seu passo tímido / Subiu a construção como se fosse máquina..."',
                'enunciado': 'Na antológica canção "Construção", o eu lírico narra os últimos momentos de um operário. A substituição constante da palavra final de cada verso por proparoxítonas diferentes ao longo das estrofes tem o efeito semântico de:',
                'alternativa_correta': 'B',
                'alternativa_a': 'Valorizar a profissão do operário da construção civil, romantizando seu sacrifício pela família e pelo progresso urbano.',
                'alternativa_b': 'Demonstrar a coisificação e alienação do trabalhador, reduzido a uma engrenagem na lógica do sistema capitalista.',
                'alternativa_c': 'Fazer uma homenagem aos ritmos musicais estrangeiros que influenciaram a MPB na década de 1970.',
                'alternativa_d': 'Atenuar a tragédia da morte do trabalhador, transformando o acidente em um evento banal e cômico cotidiano.',
                'alternativa_e': 'Criticar exclusivamente a falta de equipamentos de segurança (EPIs) nas grandes obras do "Milagre Econômico".',
                'categoria': 'Fuvest',
                'disciplina': 'Literatura',
                'habilidade_enem': 'H16'
            },
            {
                'titulo_musica': 'Que País É Este',
                'artista': 'Legião Urbana',
                'letra': '"Nas favelas, no Senado / Sujeira pra todo lado / Ninguém respeita a Constituição / Mas todos acreditam no futuro da nação / Que país é este?"',
                'enunciado': 'A letra da música, embora escrita no final da década de 1970, foi gravada e se tornou um hino na década de 1980. O principal paradoxo apontado pela banda em relação à sociedade brasileira é:',
                'alternativa_correta': 'D',
                'alternativa_a': 'A igualdade de condições de vida entre os moradores de favelas e os senadores da República.',
                'alternativa_b': 'A descrença total nas leis do país associada a uma profunda apatia política que impede qualquer mudança social.',
                'alternativa_c': 'O respeito absoluto à Constituição Federal que contrasta com as condições precárias de moradia nas periferias.',
                'alternativa_d': 'A convivência entre a corrupção estrutural e a miséria, contrastando com um otimismo acrítico em relação ao futuro.',
                'alternativa_e': 'O foco exclusivo do governo na construção civil, ignorando problemas crônicos como inflação e saúde pública.',
                'categoria': 'Enem',
                'disciplina': 'Sociologia',
                'habilidade_enem': 'H22'
            }
        ]

        # Inserindo no banco de dados (Supabase)
        for data in questoes_data:
            nova_questao = Questao(**data)
            db.session.add(nova_questao)
        
        db.session.commit()
        print("✅ SUCESSO! 4 Questões inseridas com sucesso no banco de dados!")
        print("🎮 O seu ProvaPop! já tem conteúdo para rodar a Primeira Partida do Dia!")

if __name__ == '__main__':
    popular_banco()
