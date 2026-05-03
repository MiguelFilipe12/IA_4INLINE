import math
import matplotlib.pyplot as plt
import networkx as nx

class Node:
    def __init__(self, max_depth = None):
        self.attribute = None
        self.max_depth = max_depth
        self.children = {}
        self.is_leaf  = False
        self.label = None

    def entropy (self, examples):
        total = len(examples) #Total de exemplos
        if total == 0:
            return 0 
        count = {} #Contar a frequência de cada classe
        for example in examples:
            label = example["label"]
            if label not in count: #se ainda não tiver a classe, inicializa com 0
                count[label] = 0
            count[label] += 1
 
        ent = 0                     
        for label in count: # calcula a entropia
            p = count[label] / total #probabilidade da classe
            if p == 0:
                continue
            ent -= p * math.log2(p) #entropia da classe
        return ent
    
    def information_gain(self, examples, attribute):
        entropy_before = self.entropy(examples) #Entropia antes de dividir os exemplos pelo atributo
        subsets = {} #Dividir os exemplos em subsets com base no valor do atributo
        entropy_after = 0 
        for example in examples: #Para cada exemplo (Linha do dataset)
            value = example[attribute] #Obter o valor do atributo para o exemplo
            if value not in subsets:
                subsets[value] = []
            subsets[value].append(example) # Adicionar o exemplo ao subset que corresponde ao valor do atributo

        for value in subsets: #Percorrer cada subset
            p = len(subsets[value]) / len(examples) #Probabilidade do subset
            entropy_after += p * self.entropy(subsets[value]) #Entropia após dividir os exemplos pelo atributo 
        return entropy_before - entropy_after  #retorna o information gain            
    
    def best_attribute (self, examples, atributes): #Atributes é uma lista com os nomes das colunas ainda nao usadas no split
        best_atribute = None
        best_gain = -1
        for attribute in atributes: #percorre os atributos
            gain = self.information_gain(examples, attribute) #calcula o information gain se o split for feito com esse atributo
            if gain > best_gain:
                best_gain = gain
                best_atribute = attribute
        return best_atribute #retorna o atributo com o maior information gain
    
    def majority_label(self, examples): #retorna a classe majoritária dos exemplos (a classe mais frequente)
        count = {}
        for example in examples:
            label = example["label"]
            if label not in count:
                count[label] = 0
            count[label] += 1
        majority_label = None
        majority_count = -1
        for label, c in count.items():
            if c > majority_count:
                majority_count = c
                majority_label = label
        return majority_label


    def build_tree(self, examples, atributes, depth):
        labels = set(example["label"] for example in examples) #Obter as classes presentes nos exemplos

        if len(labels) == 1:
            self.is_leaf = True
            self.label = labels.pop() #Se só tiver uma classe, torna-se uma folha com essa classe como label
            return self
        
        if not atributes:
            self.is_leaf = True
            self.label = self.majority_label(examples) #Se não tiver mais atributos para dividir, torna-se uma folha com a classe majoritária dos exemplos
            return self

        if self.max_depth is not None and depth >= self.max_depth:
            self.is_leaf = True
            self.label = self.majority_label(examples)
            return self
        
        best_atribute = self.best_attribute(examples, atributes) #Seleciona o melhor atributo para dividir os exemplos
        self.attribute = best_atribute
        subsets = {}
        for example in examples:
            value = example[best_atribute]
            if value not in subsets:
                subsets[value] = []
            subsets[value].append(example) #Dividir os exemplos em subsets com base no valor do melhor atributo
        self.label = self.majority_label(examples) #Define o label do nó como a classe majoritária dos exemplos (para o caso de não ter um filho correspondente ao valor do atributo)
        for value, subset in subsets.items():
            
            child = Node(self.max_depth)
            child.build_tree(subset, [a for a in atributes if a != best_atribute], depth + 1) #Recursivamente constrói a árvore para cada subset
            self.children[value] = child    

    def predict(self, example):
        if self.is_leaf:
            return self.label #Se for folha, retorna o label da folha
        value = example[self.attribute] #Obter o valor do atributo para o exemplo
        if value in self.children:
            return self.children[value].predict(example) #Recursivamente desce na árvore com base no valor do atributo
        else:
            return self.label #Se não tiver um filho correspondente ao valor do atributo, retorna o label do nó (classe majoritária dos exemplos)
        
    def print_tree(self, depth=0):
        indent = "  " * depth
        if self.is_leaf:
            print(f"{indent}Leaf: {self.label}")
        else:
            print(f"{indent}Node: {self.attribute}")
            for value, child in self.children.items():
                print(f"{indent}  Value: {value}")
                child.print_tree(depth + 1)

    ################################### PLOT DA ARVORE ###################################
    def _add_nodes(self, G, labels, edge_labels, parent_id, edge_label, counter):
        node_id = counter[0]
        counter[0] += 1
        
        if self.is_leaf:
            labels[node_id] = f"LEAF\n{self.label}"
        else:
            labels[node_id] = f"[{self.attribute}]"
        
        G.add_node(node_id)
        
        if parent_id is not None:
            G.add_edge(parent_id, node_id)
            edge_labels[(parent_id, node_id)] = edge_label
        
        for value, child in self.children.items():
            child._add_nodes(G, labels, edge_labels, node_id, str(value), counter)    





    def plot_tree(self):
        G = nx.DiGraph()
        labels = {}
        edge_labels = {}
        counter = [0]
        self._add_nodes(G, labels, edge_labels, None, None, counter)
        
        pos = self._hierarchy_pos(G, 0)
        
        plt.figure(figsize=(14, 8))
        nx.draw(G, pos, labels=labels, with_labels=True,
                node_color="lightblue", node_size=2000,
                font_size=8, arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        plt.title("Decision Tree (ID3)")
        plt.tight_layout()
        plt.show()

    def _hierarchy_pos(self, G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
        pos = {root: (xcenter, vert_loc)}
        children = list(G.successors(root))
        if children:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos.update(self._hierarchy_pos(G, child, width=dx,
                            vert_gap=vert_gap, vert_loc=vert_loc-vert_gap,
                            xcenter=nextx))
        return pos