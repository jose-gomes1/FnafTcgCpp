#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <ctime>

using namespace std;

enum class CardType { Animatronic, Support, Electricity };

struct Attack {
    string name;
    int cost;
    int damage;

    Attack(string n = "", int c = 0, int d = 0)
        : name(n), cost(c), damage(d) {}
};

struct Card {
    string name;
    CardType type;

    int hp = 0;
    int maxHP = 0;
    int maxElectricity = 0;
    int attachedElectricity = 0;

    string ability;
    Attack atk1;

    Card(string n = "", CardType t = CardType::Support)
        : name(n), type(t) {}
};

vector<Card> deck;
vector<Card> hand;
vector<Card> active;
vector<Card> discardPile;

bool attachedThisTurn = false;

random_device rd;
mt19937 rng(rd());

void shuffleDeck() {
    shuffle(deck.begin(), deck.end(), rng);
}

Card createEnergy() {
    return Card("Eletricidade", CardType::Electricity);
}

Card createAnim(string name, int hp, int maxE, string ability, Attack atk) {
    Card c(name, CardType::Animatronic);
    c.hp = hp;
    c.maxHP = hp;
    c.maxElectricity = maxE;
    c.ability = ability;
    c.atk1 = atk;
    return c;
}

Card createSupport(string name, string desc) {
    Card c(name, CardType::Support);
    c.ability = desc;
    return c;
}

Card findAnim(string name) {
    if(name == "Withered Freddy")
        return createAnim(name,125,3,"Liga 1 eletricidade da mão automaticamente",
                          Attack("Microphone Smash",1,20));

    if(name == "Shadow Freddy")
        return createAnim(name,150,3,"Liga 1 eletricidade da mão automaticamente",
                          Attack("Shadow Bite",1,25));

    if(name == "Jack O Bonnie")
        return createAnim(name,200,5,"Liga 1 eletricidade da mão automaticamente",
                          Attack("Flame Strike",2,40));

    if(name == "Jack O Chica")
        return createAnim(name,200,5,"Liga 1 eletricidade da mão automaticamente",
                          Attack("Inferno Feast",2,50));

    return Card();
}

void buildDeck() {

    deck.clear();

    for(int i=0;i<3;i++) deck.push_back(findAnim("Withered Freddy"));
    for(int i=0;i<2;i++) deck.push_back(findAnim("Shadow Freddy"));
    for(int i=0;i<2;i++) deck.push_back(findAnim("Jack O Bonnie"));
    for(int i=0;i<2;i++) deck.push_back(findAnim("Jack O Chica"));

    for(int i=0;i<3;i++) deck.push_back(createSupport("Freddy Mask","Proteção"));
    for(int i=0;i<3;i++) deck.push_back(createSupport("William Afton","Dano aleatório"));
    for(int i=0;i<3;i++) deck.push_back(createSupport("Power Drain","Buscar animatronic"));

    for(int i=0;i<12;i++) deck.push_back(createEnergy());

    shuffleDeck();
}

void drawCard() {
    if(deck.empty()) {
        cout << "Deck vazio!\n";
        return;
    }

    Card c = deck.back();
    deck.pop_back();
    hand.push_back(c);

    cout << "Você comprou: " << c.name << endl;
}

void showHand() {
    cout << "\n=== MÃO ===\n";
    for(int i=0;i<hand.size();i++)
        cout << i << " - " << hand[i].name << endl;
}

void showActive() {
    cout << "\n=== ATIVOS ===\n";
    for(int i=0;i<active.size();i++) {
        cout << i << " - " << active[i].name
             << " HP:" << active[i].hp
             << " Energia:" << active[i].attachedElectricity
             << "/" << active[i].maxElectricity << endl;
    }
}

void showDeck() {
    cout << "\n=== DECK ===\n";

    vector<string> names;
    vector<int> counts;

    for(auto &c : deck) {
        auto it = find(names.begin(), names.end(), c.name);
        if(it != names.end()) {
            counts[distance(names.begin(),it)]++;
        } else {
            names.push_back(c.name);
            counts.push_back(1);
        }
    }

    for(int i=0;i<names.size();i++)
        cout << names[i] << " x" << counts[i] << endl;

    cout << "Total: " << deck.size() << endl;
}

void showDiscardPile() {
    cout << "\n=== DESCARTE ===\n";

    if(discardPile.empty()) {
        cout << "Vazio.\n";
        return;
    }

    vector<string> names;
    vector<int> counts;

    for(auto &c : discardPile) {
        auto it = find(names.begin(), names.end(), c.name);
        if(it != names.end()) {
            counts[distance(names.begin(),it)]++;
        } else {
            names.push_back(c.name);
            counts.push_back(1);
        }
    }

    for(int i=0;i<names.size();i++)
        cout << names[i] << " x" << counts[i] << endl;
}

void playAnim() {
    showHand();
    int i;
    cout << "Escolha animatronic para colocar ativo: ";
    cin >> i;

    if(i>=0 && i<hand.size() && hand[i].type==CardType::Animatronic) {
        active.push_back(hand[i]);
        cout << hand[i].name << " colocado ativo.\n";
        hand.erase(hand.begin()+i);
    }
}

void useAbility() {

    if(active.empty()) {
        cout << "Nenhum animatronic ativo.\n";
        return;
    }

    showActive();
    int i;
    cout << "Escolha ativo: ";
    cin >> i;

    if(i < 0 || i >= active.size())
        return;

    Card &c = active[i];

    if(c.attachedElectricity >= c.maxElectricity) {
        cout << "Já tem energia máxima.\n";
        return;
    }

    // 🔍 Procurar eletricidade no deck
    auto it = find_if(deck.begin(), deck.end(),
        [](Card &x){ return x.type == CardType::Electricity; });

    if(it == deck.end()) {
        cout << "Nenhuma eletricidade restante no deck!\n";
        return;
    }

    // 🔋 Anexar energia
    c.attachedElectricity++;

    cout << "Eletricidade retirada do deck e ligada a "
         << c.name << " ("
         << c.attachedElectricity << "/"
         << c.maxElectricity << ")\n";

    // ❌ Remover do deck
    deck.erase(it);

    // 🔀 Baralhar deck depois da busca
    shuffleDeck();
}

void editActiveHP() {

    if(active.empty()) {
        cout << "Nenhum animatronic ativo.\n";
        return;
    }

    showActive();

    int i;
    cout << "Escolha animatronic para editar HP: ";
    cin >> i;

    if(i < 0 || i >= active.size())
        return;

    int value;
    cout << "Digite valor (negativo = dano, positivo = cura): ";
    cin >> value;

    active[i].hp += value;

    if(active[i].hp > active[i].maxHP)
        active[i].hp = active[i].maxHP;

    cout << active[i].name << " agora está com "
         << active[i].hp << " HP.\n";

    // Se morrer
    if(active[i].hp <= 0) {

        cout << active[i].name << " foi derrotado!\n";

        // Mandar energias anexadas para o descarte
        for(int e = 0; e < active[i].attachedElectricity; e++)
            discardPile.push_back(createEnergy());

        discardPile.push_back(active[i]);
        active.erase(active.begin() + i);
    }
}

void discardCard() {

    cout << "\n0-Mão\n1-Ativo inteiro\n2-Energia de ativo\n";
    int op;
    cin >> op;

    if(op==0) {
        showHand();
        int i; cin>>i;
        if(i>=0 && i<hand.size()) {
            discardPile.push_back(hand[i]);
            hand.erase(hand.begin()+i);
        }
    }

    else if(op==1) {
        showActive();
        int i; cin>>i;
        if(i>=0 && i<active.size()) {

            for(int e=0;e<active[i].attachedElectricity;e++)
                discardPile.push_back(createEnergy());

            discardPile.push_back(active[i]);
            active.erase(active.begin()+i);
        }
    }

    else if(op==2) {
        showActive();
        int i; cin>>i;
        if(i>=0 && i<active.size()) {
            int amt;
            cout << "Quantas energias remover? ";
            cin >> amt;

            if(amt>active[i].attachedElectricity)
                amt=active[i].attachedElectricity;

            active[i].attachedElectricity-=amt;

            for(int e=0;e<amt;e++)
                discardPile.push_back(createEnergy());
        }
    }
}

void mulligan() {

    int mulligans = 0;

    while(true) {

        bool hasAnim = false;
        for(auto &c : hand)
            if(c.type==CardType::Animatronic)
                hasAnim = true;

        if(hasAnim || mulligans>=3) break;

        mulligans++;

        cout << "Mulligan #" << mulligans << endl;

        for(auto &c : hand)
            deck.push_back(c);

        hand.clear();
        shuffleDeck();

        for(int i=0;i<3;i++)
            drawCard();
    }

    if(mulligans>=3) {
        cout << "Garantindo animatronic...\n";

        auto it = find_if(deck.begin(),deck.end(),
            [](Card &c){return c.type==CardType::Animatronic;});

        if(it!=deck.end()) {
            hand.push_back(*it);
            deck.erase(it);
        }
    }
}

int main() {

    buildDeck();

    for(int i=0;i<3;i++)
        drawCard();

    mulligan();

    int op;

    while(true) {

        cout << "\n--- MENU ---\n";
        cout << "1-Ver mão\n";
        cout << "2-Comprar\n";
        cout << "3-Colocar ativo\n";
        cout << "4-Ver ativos\n";
        cout << "5-Editar HP de ativo\n";
        cout << "6-Usar habilidade\n";
        cout << "7-Ver deck\n";
        cout << "8-Descartar\n";
        cout << "9-Ver descarte\n";
        cout << "10-Sair\n";

        cin >> op;

        if(op==1) showHand();
        else if(op==2) drawCard();
        else if(op==3) playAnim();
        else if(op==4) showActive();
        else if(op==5) editActiveHP();
        else if(op==6) useAbility();
        else if(op==7) showDeck();
        else if(op==8) discardCard();
        else if(op==9) showDiscardPile();
        else if(op==10) break;
    }
}