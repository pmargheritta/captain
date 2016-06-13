#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
from random import randint
import irc.bot
import json
import re

# Fonctions utilitaires

def nm2n(masque):
    '''Transforme un masque en nom d'utilisateur'''
    return masque.split('!')[0]

# Classe du bot

class Captain(irc.bot.SingleServerIRCBot):
    def __init__(self, params):
        '''Connexion au serveur'''
        self.canal = params['canal']
        self.params = params
        self.silence = False
        self.listes = {}
        self.smileys = {'content': r'[:=]-?\)', 'triste': r'[:=]-?\(', 'rire': r'[:=]-?D', 'clin': r';-?\)', \
                'langue': r'[:=]-?P', 'pleure': r'[:=]\'[)(]', 'bof': r'[:=]-?[\\/]', 'surprise': r'[:=]-?O', \
                'lunettes': r'8-?[)(]', 'bonne_hum': r'\^\^', 'agace': r'-_-', 'victoire': r'\\o/'}
        irc.bot.SingleServerIRCBot.__init__(self, [(params['serveur'], params['port'])], params['pseudo'], params['nom'])
    
    def pseudo_bot(self, pseudo):
        '''Détermine si un pseudo donné appartient au bot'''
        return pseudo.lower() == self.params['pseudo'].lower() \
                or pseudo.lower() == (self.params['prefixe_silence'] + self.params['pseudo']).lower()

    def log(self, nom, *remp):
        '''Écrit une ligne à la fin du log'''
        fichier = open('log', 'a')
        args = (str(datetime.now()),) + remp
        ligne = (self.params['log_temps'] + self.params['log_' + nom] + '\n').format(*args)
        fichier.write(ligne)
    
    def baffe(self, serv, pseudo):
        '''Envoie une baffe à un utilisateur'''
        if not self.silence and not self.jeu_en_cours:
            serv.privmsg(self.canal, pseudo + self.params['sep'] + self.params['baffe_reaction'])
            serv.action(self.canal, self.params['baffe_action'].format(pseudo))
            self.log('baffe', pseudo)
    
    def insulter(self, serv, fichier, cible, pseudo=''):
        '''Renvoie une insulte'''

        insulte = ''

        if not self.silence and not self.jeu_en_cours:
            # Génération de la liste d’insultes
            if fichier not in self.listes:
                self.listes[fichier] = [message.replace(self.params['sep_fichier'], self.params['ponctuation']) \
                for message in open(fichier).readlines()]
            liste = self.listes[fichier]
            
            # Renvoie une insulte aléatoire
            insulte = liste[randint(0, len(liste) - 1)]
            if pseudo:
                message = pseudo + self.params['sep'] + insulte
            else:
                message = insulte
            serv.privmsg(cible, message)
            self.log('insulte', cible, message)

        return insulte
    
    def mots_dictee(self, match_dictee):
        '''Renvoie une liste de mots pour la dictée'''
        
        # Génération de la liste d’insultes
        if 'dictee' not in self.listes:
            self.listes['dictee'] = [message.strip() \
            for message in open(self.params['messages_perso']).readlines() + open(self.params['messages_tous']).readlines() \
            if ' ' not in message and '’' not in message]
        liste = self.listes['dictee']
        
        # Renvoie une liste aléatoire de mots (10 par défaut)
        match = match_dictee.groups()[0]
        longueur = int(match) if match else 10
        mots = []
        if longueur < 10000:
            for i in range(longueur):
                mots.append(liste[randint(0, len(liste) - 1)])
        return mots
    
    def envoyer_mot(self, serv, mots):
        '''Propose aux joueurs d’écrire un mot'''
        mot = mots[0]
        serv.privmsg(self.canal, self.params['dictee_mot'].format(mot))
        self.log('dictee_demande', mot)
    
    def terminer_dictee(self, serv):
        '''Affichage des scores de la dictée et réinitialisation''' 
        self.scores = sorted([(self.scores[i], i) for i in self.scores], reverse=True)
        if self.scores:
            scores = self.params['dictee_sep'].join([self.params['dictee_score'].format(i[1], i[0]) for i in self.scores])
            serv.privmsg(self.canal, self.params['dictee_fin'].format(scores))
            self.log('dictee_scores', scores)
        self.init_jeux()
    
    def mot_correct(self, serv, joueur):
        '''Propose un nouveau mot ou termine la dictée'''
        
        self.log('dictee_correct', joueur)
        if joueur in self.scores:
            self.scores[joueur] += 1
        else:
            self.scores[joueur] = 1
        
        self.mots.pop(0)
        if self.mots:
            # Proposer un nouveau mot
            self.envoyer_mot(serv, self.mots)
        else:
            self.terminer_dictee(serv)
            
    def init_jeux(self):
        '''Réinitialise les jeux'''
        self.jeu_en_cours = False
        self.mots = []
        self.scores = {}
        self.log('jeux_init')
    
    def repondre_smiley(self, serv, ev):
        '''Réagit à la détection d’un smiley'''
        
        pseudo = nm2n(ev.source)
        message = ev.arguments[0]
        
        matchs = {cle: re.search(r'(^|\s+){}(\s+|$)'.format(valeur), message, re.IGNORECASE) \
                for (cle, valeur) in self.smileys.items()}
        for (smiley, match) in matchs.items():
            if match and not self.silence and not self.jeu_en_cours:
                reponse = pseudo + self.params['sep'] + self.params['smiley_' + smiley]
                serv.privmsg(self.canal, reponse)
                self.log('smiley', pseudo, smiley)
    
    def on_action(self, serv, ev):
        '''Réagit aux actions'''
        
        self.log('action', nm2m(ev.source), ev.arguments[0])
        self.repondre_smiley(serv, ev)
        
        if nm2n(ev.source) == 'ptichaton' and ev.arguments[0] == 'est un perroquet bavard':
            # Arrête le mode perroquet de ptichaton
            serv.privmsg(self.canal, 'ptichaton: arrête le perroquet')
            self.log('ptichaton')
        else:
            # Envoie une insulte personnelle lors d’une action
            self.insulter(serv, self.params['messages_perso'], self.canal, nm2n(ev.source))
    
    def on_invite(self, serv, ev):
        '''Joint le canal lors d’une invitation'''
        if self.pseudo_bot(ev.target):
            self.log('invite', ev.arguments[0], nm2n(ev.source))
            if self.canal:
                serv.part(self.canal, self.params['quitte'])
            serv.join(ev.arguments[0])
    
    def on_join(self, serv, ev):
        '''Envoie une insulte collective lors de l’arrivée sur le canal'''
        pseudo = nm2n(ev.source)
        if self.pseudo_bot(pseudo):
            self.canal = ev.target
            self.log('join', self.canal)
            self.init_jeux()
            self.insulter(serv, self.params['messages_tous'], self.canal)
    
    def on_kick(self, serv, ev):
        '''Rejoint automatiquement le canal après le kick'''
        self.log('kick', ev.target, nm2n(ev.source), ev.arguments[1])
        if self.pseudo_bot(ev.arguments[0]):
            serv.join(self.canal)
    
    def on_nick(self, serv, ev):
        '''Envoie une insulte collective lors de l’activation du mode normal'''
        if ev.target == self.params['pseudo']:
            self.log('parle')
            self.insulter(serv, self.params['messages_tous'], self.canal)
        elif ev.target == self.params['prefixe_silence'] + self.params['pseudo']:
            self.log('silence')
    
    def on_part(self, serv, ev):
        '''Enregistre le départ du canal'''
        pseudo = nm2n(ev.source)
        if self.pseudo_bot(pseudo):
            self.log('part', self.canal)
            self.canal = ''
    
    def on_privmsg(self, serv, ev):
        '''Réagit aux messages personnels'''
        source = nm2n(ev.source)
        message = ev.arguments[0]
        
        # Écrit la requête dans le canal
        match_msg = re.search(r'!msg\s+(.*)', message, re.IGNORECASE)
        match_act = re.search(r'!act\s+(.*)', message, re.IGNORECASE)
        if match_msg:
            requete = match_msg.groups()[0]
            self.log('req_msg', source, requete)
            if source == self.params['proprietaire']:
                serv.privmsg(self.canal, requete)
            return
        elif match_act:
            requete = match_act.groups()[0]
            self.log('req_act', source, requete)
            if source == self.params['proprietaire']:
                serv.action(self.canal, requete)
            return
        
        # Enregistre les messages personnels
        self.log('privmsg', source, message)
    
    def on_pubmsg(self, serv, ev):
        '''Réagit aux messages publiés'''
        source = nm2n(ev.source)
        message = ev.arguments[0]
        
        # Réagit aux smileys
        self.repondre_smiley(serv, ev)
        
        # Réagit à l’écriture d’un mot correct pendant le jeu
        if self.jeu_en_cours and message.lower().strip() == self.mots[0].lower():
            self.mot_correct(serv, source)
            return
        
        # Arrêt du jeu, kick et arrêt du bot
        match_stop = re.search(self.params['pseudo'] + r'[:,\s]+stop', message, re.IGNORECASE)
        match_sors = re.search(self.params['pseudo'] + r'[:,\s]+sors', message, re.IGNORECASE)
        match_meurs = re.search(self.params['pseudo'] + r'[:,\s]+meurs', message, re.IGNORECASE)
        if match_stop:
            self.log('req_stop', source)
            if self.jeu_en_cours:
                serv.action(self.canal, self.params['jeu_stop'])
                self.terminer_dictee(serv)
            else:
                self.baffe(serv, source)
            return
        elif match_sors:
            self.log('req_sors', self.canal, source)
            serv.part(self.canal, self.params['quitte'])
            return
        elif match_meurs:
            self.log('req_meurs', source)
            if source == self.params['proprietaire']:
                self.die(msg=self.params['quitte'])
            else:
                self.baffe(serv, source)
            return
        
        # Rechargement des paramètres
        match_charge = re.search(self.params['pseudo'] + r'[:,\s]+charge', message, re.IGNORECASE)
        if match_charge:
            self.log('req_charge', source)
            self.params = json.load(open('params.json'))
            serv.action(self.canal, self.params['charge'])
            self.log('charge')
            return
        
        # Mode silence
        match_silence = re.search(self.params['pseudo'] + r'[:,\s]+silence', message, re.IGNORECASE)
        match_parle = re.search(self.params['pseudo'] + r'[:,\s]+parle', message, re.IGNORECASE)
        if match_silence:
            self.log('req_silence', source)
            if self.silence:
                self.baffe(serv, source)
            else:
                # Activation du mode silence
                self.silence = True
                serv.nick(self.params['prefixe_silence'] + self.params['pseudo'])
            return
        elif match_parle:
            self.log('req_parle', source)
            if self.silence:
                # Activation du mode normal
                self.silence = False
                serv.nick(self.params['pseudo'])
            else:
                self.baffe(serv, source)
            return
        
        # Dictée
        match_dictee = re.search(self.params['pseudo'] + r'[:,\s]+dictée(?:\s+([0-9]+))?', message, re.IGNORECASE)
        match_rappel = re.search(self.params['pseudo'] + r'[:,\s]+rappel', message, re.IGNORECASE)
        if match_dictee and not self.jeu_en_cours:
            self.log('req_dictee', source)
            self.mots = self.mots_dictee(match_dictee)
            if not self.mots:
                self.baffe(serv, source)
            else:
                self.jeu_en_cours = True
                self.envoyer_mot(serv, self.mots)
            return
        if match_rappel:
            self.log('req_rappel', source)
            if self.jeu_en_cours:
                self.envoyer_mot(serv, self.mots)
            else:
                self.baffe(serv, source)
            return
        
        # Envoie une insulte par MP ou une insulte personnelle lors de l’évocation de son nom
        match_insulte = re.search(self.params['pseudo'] + r'[:,\s]+insulte(?:\s+(\w+))?', message, re.IGNORECASE)
        if match_insulte:
            cible = match_insulte.groups()[0]
            self.log('req_insulte', cible, source)
            if not cible or self.pseudo_bot(cible) or cible.lower() == self.params['proprietaire'].lower():
                self.baffe(serv, source)
            else:
                # Insulter et recopier l’insulte en MP
                if not self.silence and not self.jeu_en_cours:
                    insulte = self.insulter(serv, self.params['messages_perso'], cible)
                    serv.privmsg(source, self.params['mp_cible'].format(cible, insulte))
            return
        elif self.params['pseudo'].lower() in message.lower():
            self.log('mention', source)
            self.insulter(serv, self.params['messages_perso'], self.canal, source)
            return
    
    def on_welcome(self, serv, ev):
        '''Joint le canal à la connexion au serveur'''
        self.log('welcome', self.params['serveur'], self.params['port'], self.params['pseudo'])
        serv.join(self.canal, self.params['mdp'])

# Chargement des paramètres
captain = Captain(json.load(open('params.json')))

# Démarrage et arrêt du bot par Ctrl+C
try:
    captain.start()
except KeyboardInterrupt:
    captain.die(msg=captain.params['quitte'])
