"""Tour PC dessinée en 2D : pièces cliquables, connecteurs et flux d'air."""
import math
import pygame
from . import config as C
from .pc_builder import PARTS

# Zones de pose. Les étapes superposées utilisent uniquement la zone sélectionnée.
ZONES={
 'case':(304,143,510,620),'board':(377,230,310,355),
 'cpu':(464,292,86,80),'paste':(464,292,86,80),
 'ram':(590,273,55,154),'ssd':(462,424,115,26),
 'cooler':(447,273,121,133),'gpu':(395,484,292,73),
 'psu':(340,641,245,84),'fans':(717,217,77,344),
 'atx':(663,300,23,100),'eps':(406,236,75,22),'pcie':(611,482,58,24),
}

def fan(s,x,y,r,t,on=False):
    pygame.draw.circle(s,(9,17,29),(x,y),r)
    pygame.draw.circle(s,(64,223,201) if on else (85,114,149),(x,y),r,3)
    for n in range(7):
        a=n*math.tau/7+(t*3 if on else .2)
        pts=[(x+math.cos(a)*r*.24,y+math.sin(a)*r*.24),
             (x+math.cos(a+.12)*r*.85,y+math.sin(a+.12)*r*.85),
             (x+math.cos(a+.65)*r*.75,y+math.sin(a+.65)*r*.75),
             (x+math.cos(a+.5)*r*.32,y+math.sin(a+.5)*r*.32)]
        pygame.draw.polygon(s,(48,69,91),pts)
    pygame.draw.circle(s,(92,120,147),(x,y),round(r*.22))

def render_pc(v,b,selected,mouse,guide=True,confirm=False):
    s=v.canvas; done=b.installed; on=b.booted
    v.buttons.clear(); s.blit(v.background,(0,0))
    v.text('ATELIER ARCHITECTURE',(27,25),36,C.TEAL)
    v.text('Montage PC · Manipule, observe, explique.',(28,68),22,C.MUTED)
    v.button('hub','Chantier',(925,27,167,43),mouse)
    v.panel((24,110,247,683))
    v.text('LES COMPOSANTS',(42,130),22,C.TEAL)
    for i,(key,p) in enumerate(PARTS.items()):
        y=169+i*40
        v.button('pc:select:'+key,('[OK]  ' if key in done else '+  ')+p.short,(38,y,219,33),mouse,key==selected)
    v.wrapped('Choisis une pièce puis clique son emplacement dans la tour.',43,712,205,20,C.MUTED,24)
    # Boîtier ouvert : profondeur, pieds, panneaux et compartiment PSU.
    pygame.draw.polygon(s,(25,34,48),[(304,143),(782,143),(813,168),(813,760),(304,760)])
    pygame.draw.rect(s,(54,70,88) if 'case' in done else (30,40,54),(304,143,478,617),border_radius=13)
    pygame.draw.rect(s,(12,20,32),(319,182,446,555),border_radius=9)
    pygame.draw.rect(s,(45,61,79),(330,756,52,14),border_radius=4)
    pygame.draw.rect(s,(45,61,79),(701,756,52,14),border_radius=4)
    pygame.draw.line(s,C.TEAL if on else (67,92,114),(327,166),(728,166),3)
    pygame.draw.circle(s,C.TEAL if on else C.ORANGE,(748,164),6,2)
    v.text('NOVA / OPEN LAB',(339,150),20,C.TEXT)
    pygame.draw.rect(s,(24,34,48),(326,614,431,117),border_radius=6)
    v.text('ALIMENTATION',(611,682),16,C.MUTED)
    if 'case' not in done:
        v.wrapped('Pose le boîtier pour commencer.',391,350,286,32,C.MUTED,36)
    if 'board' in done:
        pygame.draw.rect(s,(24,75,77),(377,230,310,355),border_radius=6)
        pygame.draw.rect(s,(65,135,132),(377,230,310,355),2,border_radius=6)
        for k in range(10):
            col=(37,100,101)
            pygame.draw.lines(s,col,False,[(385,273+k*23),(420+k*5,273+k*23),(440+k*5,293+k*23),(675,293+k*23)],1)
        for x,y in ((386,239),(677,239),(386,574),(677,574)):
            pygame.draw.circle(s,(178,189,185),(x,y),3)
        for x,y in ((396,274),(415,274),(434,274),(397,406),(416,406)):
            pygame.draw.rect(s,(45,53,67),(x,y,13,25),border_radius=2)
        pygame.draw.rect(s,(43,52,61),ZONES['cpu'],border_radius=4)
        pygame.draw.rect(s,(173,179,173),ZONES['cpu'],2,border_radius=4)
        for x in (590,620): pygame.draw.rect(s,(8,20,28),(x,273,20,154),border_radius=3)
        pygame.draw.rect(s,(9,23,31),(399,490,271,13),border_radius=2)
        pygame.draw.rect(s,(10,30,38),ZONES['ssd'],border_radius=2)
        pygame.draw.rect(s,(219,177,87),(663,300,20,100),2)
        pygame.draw.rect(s,(219,177,87),ZONES['eps'],2)
        pygame.draw.circle(s,(174,190,195),(638,553),16)
        v.text('M.2',(583,429),16,C.MUTED)
    if 'cpu' in done:
        pygame.draw.rect(s,(173,186,199),(472,300,70,64),border_radius=3)
        pygame.draw.rect(s,(215,225,232),(480,308,54,48),border_radius=3)
        v.text('CPU',(507,331),22,(30,46,61),True)
    if 'paste' in done:
        pygame.draw.circle(s,(211,216,225),(508,332),8)
    if 'ram' in done:
        for x in (592,622):
            pygame.draw.rect(s,(53,79,106),(x,274,16,152),border_radius=3)
            for y in range(290,413,22):pygame.draw.rect(s,(17,25,39),(x+3,y,10,17),border_radius=2)
            pygame.draw.line(s,(158,125,244),(x+4,281),(x+12,281),3)
    if 'ssd' in done:
        pygame.draw.rect(s,(26,36,53),(463,425,113,24),border_radius=3)
        pygame.draw.rect(s,(200,208,212),(480,429,66,16),border_radius=2)
        v.text('NVMe',(487,430),16,(35,47,66))
        pygame.draw.circle(s,(191,170,111),(568,437),3)
    if 'cooler' in done:
        pygame.draw.rect(s,(98,114,130),(448,274,118,131),border_radius=7)
        for y in range(279,400,7):pygame.draw.line(s,(49,66,82),(454,y),(560,y),2)
        fan(s,507,338,49,v.world_time,on)
        pygame.draw.lines(s,(225,190,100),False,[(562,284),(574,284),(574,261),(548,261)],2)
    if 'gpu' in done:
        pygame.draw.rect(s,(33,45,64),(395,484,292,73),border_radius=7)
        pygame.draw.rect(s,(83,109,137),(395,484,292,73),2,border_radius=7)
        fan(s,449,521,28,v.world_time,on);fan(s,527,521,28,v.world_time,on)
        pygame.draw.line(s,(171,119,251),(576,537),(671,537),3)
        v.text('GPU',(600,507),24,C.TEXT)
        pygame.draw.rect(s,(181,171,143),(611,482,58,10),border_radius=2)
    if 'psu' in done:
        pygame.draw.rect(s,(54,67,84),ZONES['psu'],border_radius=6)
        fan(s,389,683,32,0,False)
        v.text('PSU',(444,658),28,C.TEXT)
        v.text('AC → DC',(445,697),20,C.TEAL)
    if 'fans' in done:
        for y in (262,391,520): fan(s,751,y,34,v.world_time,on)
        fan(s,345,252,22,v.world_time,on)
        # Flux avant vers arrière, uniquement quand le PC fonctionne.
        if on:
            for y in (262,391,520):
                x=704-int(v.world_time*34)%65
                pygame.draw.line(s,C.TEAL,(x+17,y),(x,y),2)
                pygame.draw.lines(s,C.TEAL,False,[(x+6,y-5),(x,y),(x+6,y+5)],2)
    cables={
      'atx':([(570,668),(704,668),(704,350),(675,350)],(86,218,199)),
      'eps':([(560,656),(353,656),(353,214),(444,214),(444,246)],(238,184,88)),
      'pcie':([(578,684),(697,684),(697,467),(641,467),(641,487)],(175,133,241)),
    }
    for k,(pts,col) in cables.items():
        if k in done:
            pygame.draw.lines(s,(8,13,22),False,pts,10)
            pygame.draw.lines(s,col,False,pts,4)
            pygame.draw.rect(s,col,(*pts[-1],10,10),border_radius=2)
    if selected and guide:
        rect=pygame.Rect(ZONES[selected])
        pygame.draw.rect(s,C.TEAL if selected in done else C.ORANGE,rect.inflate(8,8),2,border_radius=6)
        label=PARTS[selected].destination
        v.text(label,(550,793),22,C.TEAL,True)
        if selected not in done:
            v.text('Clique ici',(rect.centerx,rect.top-18),18,C.ORANGE,True)
    v.panel((839,110,257,683),C.TEAL)
    v.text('COMPRENDRE',(856,130),22,C.TEAL)
    if selected:
        p=PARTS[selected]
        v.wrapped(p.title,856,172,221,28,C.TEXT,30)
        v.wrapped(p.role,856,248,221,20,C.MUTED,23)
        v.text('QUESTION POUR LA CLASSE',(856,524),16,C.ORANGE)
        v.wrapped(p.question,856,552,221,20,C.TEXT,26)
        v.button('pc:remove','Retirer cette pièce',(855,685,225,38),mouse)
    else:
        v.wrapped('Un PC complet : calcul, mémoire, stockage, énergie et refroidissement.',856,182,220,28,C.TEXT,32)
        v.wrapped('Sélectionne une pièce pour découvrir son rôle. Le guide peut être masqué pour te tester.',856,366,220,22,C.MUTED,27)
    v.text(f'{len(done)} / {len(PARTS)} étapes',(855,749),26,C.TEAL)
    v.button('pc:guide','Guide : '+('ON' if guide else 'OFF'),(25,816,179,42),mouse)
    v.button('pc:reset','Recommencer',(218,816,190,42),mouse)
    v.button('pc:boot','Démarrer le PC',(427,816,278,42),mouse,True)
    v.text('POST OK' if on else 'PC hors tension',(858,827),26,C.TEAL if on else C.MUTED)
    if on:
        v.text('Matériel prêt · Système à installer sur le SSD',(550,116),20,C.TEAL,True)
    if confirm:
        shade=pygame.Surface((1120,900),pygame.SRCALPHA);shade.fill((2,9,17,225));s.blit(shade,(0,0))
        v.buttons.clear();v.panel((260,260,600,330),C.ORANGE)
        v.text('Recommencer le montage ?',(560,303),36,C.TEXT,True)
        v.wrapped('Seul le montage PC sera vidé. Ta campagne et tes crédits sont conservés.',300,373,520,26,C.MUTED,30)
        v.button('pc:cancel','Continuer',(300,503,233,46),mouse)
        v.button('pc:confirm','Vider le boîtier',(551,503,269,46),mouse,True)
    v.toast_layer()
    return s
