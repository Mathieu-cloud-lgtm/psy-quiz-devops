# questions.py
from typing import List, Dict, Any

PROFILES = {
    0: "Rêveur",
    1: "Inventif",
    2: "Logique",
    3: "Social",
    4: "Aventurier",
    5: "Organisé",
    6: "Sensible",
    7: "Confiant",
    8: "Calme",
    9: "Optimiste"
}

PROFILE_DETAILS = {
    0: {
        "description": "Vous possédez une imagination débordante...",
        "advice": "Cultivez votre créativité...",
        "traits": ["Créatif", "Idéaliste", "Intuitif", "Rêveur éveillé"],
        "exploration": [
            "Comment votre imaginaire influence-t-il vos décisions quotidiennes ?",
            "Quels sont vos rêves les plus récurrents ?",
            "Dans quels domaines votre créativité s'exprime-t-elle le mieux ?"
        ],
        "questions": [
            "Est-ce que je passe trop de temps dans mes pensées ?",
            "Comment puis-je concrétiser une de mes idées cette semaine ?",
            "Qu'est-ce qui nourrit mon imagination ?"
        ],
        "work": [
            "Tenez un journal de vos rêves pendant 7 jours.",
            "Réalisez un projet créatif sans vous juger.",
            "Partagez une de vos idées avec quelqu'un."
        ],
        "themes": [
            "L'équilibre entre imaginaire et réalité",
            "La peur de l'échec créatif",
            "L'expression de soi à travers l'art"
        ]
    },
    1: {
        "description": "Vous êtes un esprit curieux et innovant...",
        "advice": "Entourez-vous de personnes aux profils variés...",
        "traits": ["Innovant", "Curieux", "Pragmatique", "Expérimentateur"],
        "exploration": [
            "Quelles inventions vous ont marqué ?",
            "Comment réagissez-vous face à un problème inattendu ?",
            "Dans quel domaine aimeriez-vous innover ?"
        ],
        "questions": [
            "Est-ce que je cherche trop la perfection ?",
            "Comment sortir de ma zone de confort intellectuelle ?",
            "Quelle est la dernière idée que j'ai eue ?"
        ],
        "work": [
            "Listez 10 problèmes et imaginez une solution pour chacun.",
            "Créez un prototype simple d'une de vos idées.",
            "Discutez avec une personne d'un domaine différent."
        ],
        "themes": [
            "La gestion de l'échec dans l'innovation",
            "La collaboration interdisciplinaire",
            "L'équilibre entre intuition et analyse"
        ]
    },
    2: {
        "description": "Votre force réside dans votre capacité à analyser...",
        "advice": "Faites confiance à votre raisonnement tout en restant ouvert aux intuitions.",
        "traits": ["Analytique", "Rationnel", "Méthodique", "Objectif"],
        "exploration": [
            "Comment votre esprit logique vous aide-t-il ?",
            "Y a-t-il des situations où votre logique entre en conflit avec vos émotions ?",
            "Quel est votre processus de prise de décision ?"
        ],
        "questions": [
            "Est-ce que je laisse assez de place à l'intuition ?",
            "Comment mieux intégrer les émotions dans mes analyses ?",
            "Quand ma logique m'a-t-elle trompé ?"
        ],
        "work": [
            "Prenez une décision en listant les pour/contre, puis écoutez votre ressenti.",
            "Analysez une situation passée sous un angle émotionnel.",
            "Pratiquez la méditation pour équilibrer logique et intuition."
        ],
        "themes": [
            "Le conflit entre raison et émotion",
            "La prise de décision en situation d'incertitude",
            "L'importance du doute méthodique"
        ]
    },
    3: {
        "description": "Vous êtes naturellement tourné vers les autres...",
        "advice": "Continuez à cultiver vos relations.",
        "traits": ["Empathique", "Communicatif", "Altruiste", "Chaleureux"],
        "exploration": [
            "Comment vos relations influencent-elles votre bien-être ?",
            "Vous sentez-vous submergé par les émotions des autres ?",
            "Quel rôle jouez-vous dans un groupe ?"
        ],
        "questions": [
            "Est-ce que je prends assez soin de moi en aidant les autres ?",
            "Comment mieux exprimer mes propres besoins ?",
            "Quelles relations sont les plus importantes ?"
        ],
        "work": [
            "Pratiquez l'écoute active sans interrompre.",
            "Notez chaque jour un moment où vous avez aidé quelqu'un.",
            "Fixez-vous une limite pour préserver votre énergie émotionnelle."
        ],
        "themes": [
            "L'équilibre entre donner et recevoir",
            "La gestion de l'empathie excessive",
            "L'affirmation de soi dans les relations"
        ]
    },
    4: {
        "description": "L'aventure et la découverte sont votre moteur...",
        "advice": "Saisissez les opportunités de nouvelles expériences.",
        "traits": ["Audacieux", "Spontané", "Aventurier", "Curieux du monde"],
        "exploration": [
            "Quelles sont vos plus grandes aventures ?",
            "Comment gérez-vous l'incertitude ?",
            "Qu'est-ce qui vous pousse à sortir de votre zone de confort ?"
        ],
        "questions": [
            "Est-ce que je prends trop de risques ou pas assez ?",
            "Comment intégrer plus d'aventure dans ma vie quotidienne ?",
            "Quelle peur m'empêche de vivre pleinement ?"
        ],
        "work": [
            "Planifiez une petite aventure dans le mois.",
            "Listez 10 choses que vous n'avez jamais osé faire.",
            "Tenez un journal de vos découvertes."
        ],
        "themes": [
            "La gestion du risque et de la peur",
            "L'équilibre entre stabilité et nouveauté",
            "La quête de sens à travers l'aventure"
        ]
    },
    5: {
        "description": "L'ordre et la planification sont vos maîtres-mots...",
        "advice": "Utilisez vos compétences pour structurer des projets collectifs.",
        "traits": ["Méthodique", "Discipliné", "Fiable", "Ordonné"],
        "exploration": [
            "Comment votre besoin d'ordre influence-t-il votre vie ?",
            "Y a-t-il des domaines où vous êtes trop rigide ?",
            "Que ressentez-vous face à l'imprévu ?"
        ],
        "questions": [
            "Est-ce que je laisse assez de place à la spontanéité ?",
            "Comment mieux gérer les changements de plan ?",
            "Qu'est-ce qui me stresse dans le désordre ?"
        ],
        "work": [
            "Introduisez un petit désordre dans votre routine.",
            "Planifiez une semaine sans planning.",
            "Déléguez une tâche pour apprendre à lâcher prise."
        ],
        "themes": [
            "Le besoin de contrôle et son impact",
            "La flexibilité face à l'imprévu",
            "L'organisation comme outil de bien-être"
        ]
    },
    6: {
        "description": "Vous ressentez les émotions avec intensité...",
        "advice": "Apprenez à protéger votre espace émotionnel.",
        "traits": ["Émotif", "Intuitif", "Réceptif", "Passionné"],
        "exploration": [
            "Comment votre sensibilité influence-t-elle vos relations ?",
            "Quels sont les déclencheurs de vos émotions fortes ?",
            "Comment exprimez-vous vos émotions ?"
        ],
        "questions": [
            "Est-ce que je me laisse submerger par mes émotions ?",
            "Comment mieux réguler mes émotions ?",
            "Quelles émotions ai-je du mal à accepter ?"
        ],
        "work": [
            "Tenez un journal émotionnel.",
            "Pratiquez la respiration profonde.",
            "Exprimez une émotion difficile à travers l'art."
        ],
        "themes": [
            "La régulation émotionnelle",
            "L'acceptation de la sensibilité",
            "Les relations et l'empathie"
        ]
    },
    7: {
        "description": "Vous dégagez une assurance naturelle...",
        "advice": "Votre leadership est un cadeau, mais n'oubliez pas d'écouter les avis contraires.",
        "traits": ["Leader", "Déterminé", "Charismatique", "Affirmé"],
        "exploration": [
            "Comment votre assurance influence-t-elle votre entourage ?",
            "Y a-t-il des moments où vous doutez de vous ?",
            "Comment gérez-vous la critique ?"
        ],
        "questions": [
            "Est-ce que je sais écouter les autres ?",
            "Comment rester humble dans mes réussites ?",
            "Quand ai-je été trop sûr de moi ?"
        ],
        "work": [
            "Demandez un feedback honnête à un proche.",
            "Pratiquez l'écoute active.",
            "Identifiez une situation où déléguer."
        ],
        "themes": [
            "L'équilibre entre confiance et humilité",
            "La gestion du pouvoir",
            "L'écoute dans le leadership"
        ]
    },
    8: {
        "description": "Le calme et la sérénité vous caractérisent...",
        "advice": "Votre paix intérieure est précieuse.",
        "traits": ["Paisible", "Réfléchi", "Stable", "Méditatif"],
        "exploration": [
            "Comment votre calme influence-t-il votre environnement ?",
            "Qu'est-ce qui perturbe votre sérénité ?",
            "Comment cultivez-vous votre paix intérieure ?"
        ],
        "questions": [
            "Ma tranquillité peut-elle être perçue comme de l'indifférence ?",
            "Comment mieux gérer les situations stressantes ?",
            "Qu'est-ce qui me fait perdre mon calme ?"
        ],
        "work": [
            "Pratiquez la méditation 10 minutes par jour.",
            "Dans une situation tendue, respirez profondément.",
            "Offrez votre écoute calme à quelqu'un."
        ],
        "themes": [
            "La résilience face au stress",
            "L'impact de la sérénité",
            "L'équilibre entre action et contemplation"
        ]
    },
    9: {
        "description": "Vous voyez la vie du bon côté...",
        "advice": "Gardez cette lumière, mais restez réaliste.",
        "traits": ["Positif", "Enthousiaste", "Jovial", "Motivant"],
        "exploration": [
            "Comment votre optimisme influence-t-il votre vie ?",
            "Y a-t-il des moments où vous avez du mal à rester positif ?",
            "Comment transmettez-vous votre énergie ?"
        ],
        "questions": [
            "Mon optimisme me rend-il parfois aveugle aux difficultés ?",
            "Comment garder espoir face à l'adversité ?",
            "Qu'est-ce qui nourrit ma positivité ?"
        ],
        "work": [
            "Tenez un journal de gratitude.",
            "Face à un problème, listez trois solutions.",
            "Partagez un moment de joie."
        ],
        "themes": [
            "L'équilibre entre optimisme et réalisme",
            "La résilience",
            "Le rôle de la gratitude"
        ]
    }
}

QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "text": "Face à un problème complexe, vous avez tendance à :",
        "choices": [
            {"text": "Imaginer des solutions originales", "scores": [2, 2, 1, 0, 1, 0, 0, 0, 0, 0]},
            {"text": "Analyser méthodiquement la situation", "scores": [0, 1, 2, 0, 0, 2, 0, 0, 0, 0]},
            {"text": "Demander l'avis de votre entourage", "scores": [0, 0, 0, 2, 1, 0, 1, 0, 0, 1]},
            {"text": "Vous lancer sans trop réfléchir", "scores": [0, 1, 0, 0, 2, 0, 0, 1, 0, 1]},
            {"text": "Prendre du recul et méditer", "scores": [1, 0, 1, 0, 0, 0, 1, 0, 2, 0]}
        ]
    },
    # ... (les 20 questions complètes, identiques à la version précédente, je ne recopie pas tout pour gagner de la place, mais vous devez les avoir)
    # Assurez-vous d'avoir les 20 questions avec leurs pondérations.
]