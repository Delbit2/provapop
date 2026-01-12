from app import app, db, Question
from datetime import datetime

def seed_questions():
    with app.app_context():
        questions_data = [
            {
                'song_title': 'Toda Forma de Poder',
                'artist': 'Engenheiros do Hawaii',
                'lyrics': '"E toda forma de poder\nMe inspira terror\nMe inspira horror\nDeixa eu te dizer\nPor que eu sou contra\nA toda forma de poder"',
                'statement': 'Na letra da canção "Toda Forma de Poder", dos Engenheiros do Hawaii, o compositor expressa uma crítica social. Considerando o contexto histórico e social do Brasil na década de 1980, a mensagem central da música refere-se à crítica:',
                'correct_answer': 'C',
                'option_a': 'à política partidária e aos sistemas eleitorais democráticos, defendendo uma monarquia absoluta.',
                'option_b': 'à concentração de poder nas mãos de grupos minoritários, sem questionar as estruturas sociais existentes.',
                'option_c': 'às estruturas autoritárias e à concentração de poder que limitavam as liberdades individuais e coletivas.',
                'option_d': 'exclusivamente ao poder militar, ignorando outros aspectos do contexto social e político da época.',
                'option_e': 'ao poder econômico, sem relacionar com as questões políticas e sociais do período.'
            }
        ]
        
        for q_data in questions_data:
            existing = Question.query.filter_by(song_title=q_data['song_title']).first()
            if not existing:
                question = Question(**q_data)
                db.session.add(question)
        
        db.session.commit()
        print('Questions seeded successfully!')

if __name__ == '__main__':
    seed_questions()