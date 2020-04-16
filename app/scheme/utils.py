import base64
from collections import OrderedDict
from typing import List

import graphviz


def safe_init_nodes(source: List[str], graph: graphviz.dot, name: str) -> List[str]:
    for node in source:
        graph.node(f"{name}-{node}", label=node)
    if not len(source):
        graph.node(f"{name}-fake", style='invis')
        source.append("fake")
    return source


class Node:
    def __init__(self, n_type, n_id, n_term=0, **kwargs):
        self.label = f"{n_type}-{n_id}"
        self.n_term = n_term
        if 'color' in kwargs:
            self.color = kwargs['color']
        else:
            self.color = "grey70"


class FakeNode(Node):
    def __init__(self, n_type):
        super().__init__(n_type, "fake")


class Cluster(graphviz.Digraph):
    def __init__(self, cluster_type: str,
                 field_mapping: dict,
                 serialized_data: List[dict],
                 *args, **kwargs
                 ):
        self.cluster_type = cluster_type
        self.name = f"cluster_{cluster_type}"
        self.nodes: List[Node] = []
        self.safe_init_nodes(field_mapping, serialized_data)
        super().__init__(*args, **kwargs)

    def safe_init_nodes(self, field_mapping: dict, serialized_data: List[dict]):
        for element in serialized_data:
            self.nodes.append(Node(self.cluster_type,
                                   element[field_mapping['id']],
                                   element.get(field_mapping['n_term'], 0)
                                   ))
        if len(self.nodes) == 0:
            self.nodes.append(FakeNode(self.cluster_type))


class Graph(graphviz.Digraph):
    def __init__(self, serialized_data, *args, **kwargs):
        self.inputs = Cluster("inputs",
                              {"id": "node_id",
                               "n_term": "n_terminals"},
                              serialized_data['inputs'], )


def get_img(data, debug=False):
    inp_to_split = False
    split_to_out = False

    inputs = [str(inp['node_id']) for inp in data['inputs']]
    splitters = [splt['node_id'] for splt in data['splitters']]
    outputs = [str(out['node_id']) for out in data['outputs']]
    fibers = []
    for fiber in data['fibers']:
        if fiber['from_node'] != {} and fiber['to_node'] != {}:
            if len({fiber['from_node']['node_type'], fiber['to_node']['node_type']}.symmetric_difference(
                    {"inputs", "splitters"})) == 0:
                inp_to_split = True
            if len({fiber['from_node']['node_type'], fiber['to_node']['node_type']}.symmetric_difference(
                    {"splitters", "outputs"})) == 0:
                split_to_out = True
            fibers.append((f"{fiber['from_node']['node_type']}-{fiber['from_node']['node_id']}",
                           f"{fiber['to_node']['node_type']}-{fiber['to_node']['node_id']}",
                           fiber['color'], str(fiber['id'])))
        elif fiber['from_node'] != {}:
            fibers.append((f"{fiber['from_node']['node_type']}-{fiber['from_node']['node_id']}",
                           "",
                           fiber['color'], str(fiber['id'])))
        elif fiber['to_node'] != {}:
            fibers.append(("",
                           f"{fiber['to_node']['node_type']}-{fiber['to_node']['node_id']}",
                           fiber['color'], str(fiber['id'])))

    g = graphviz.Digraph("mufta",
                         graph_attr={"rankdir": "LR",
                                     "compound": "true",
                                     "bgcolor": "transparent"
                                     },
                         format="png", )
    input_graph = graphviz.Digraph(name="cluster_inputs",
                                   graph_attr={"rank": "same",
                                               "style": "invis"
                                               },
                                   node_attr={"shape": "rarrow"})

    inputs = safe_init_nodes(inputs, input_graph, "inputs")

    g.subgraph(input_graph)

    splitter_graph = graphviz.Digraph(name="cluster_splitters",
                                      graph_attr={"rank": "same", "label": "Splitters"},
                                      node_attr={"shape": "square"})

    splitters = safe_init_nodes(splitters, splitter_graph, "splitters")

    g.subgraph(splitter_graph)

    output_graph = graphviz.Digraph(name="cluster_outputs",
                                    graph_attr={
                                        "rank": "same",
                                        "style": "invis"
                                    },
                                    node_attr={"shape": "rarrow"})

    outputs = safe_init_nodes(outputs, output_graph, "outputs")

    g.subgraph(output_graph)

    # #--------------
    #
    # g.edge("inp1", "splitter1",  color="invis", ltail="cluster_inputs", lhead="cluster_splitters")
    # g.edge("inp3", "mid2",  color="invis")
    # g.edge("inp1", "mid1",  color="blue:green")
    # g.edge("inp1", "mid2",  color="purple:red")
    # g.edge("inp2", "mid2",  color="blue")
    # g.edge("mid2", "mid3",  color="orange")
    # g.edge("splitter1", "out1",  color="invis", ltail="cluster_splitters", lhead='cluster_outs')
    # g.edge("inp1", "mid1")

    if not inp_to_split:
        g.edge(f"inputs-{inputs[len(inputs) // 2]}", f"splitters-{splitters[len(splitters) // 2]}",
               color="invis",
               ltail="cluster_inputs",
               lhead="cluster_splitters")

    if not split_to_out:
        g.edge(f"splitters-{splitters[len(splitters) // 2]}", f"outputs-{outputs[len(outputs) // 2]}",
               color="invis",
               ltail="cluster_splitters",
               lhead="cluster_outputs")

    for a, b, c, d in fibers:
        if not a:
            if "inputs" in b:
                g.edge(f"splitters-{splitters[len(splitters) // 2]}", b, color=c, ltail="cluster_splitters", label=d)
            elif "splitters" in b:
                g.edge(f"inputs-{inputs[len(inputs) // 2]}", b, color=c, ltail="cluster_inputs", label=d)
            else:
                g.edge(f"splitters-{splitters[len(splitters) // 2]}", b, color=c, ltail="cluster_splitters", label=d)
        elif not b:
            if "inputs" in a:
                g.edge(a, f"splitters-{splitters[len(splitters) // 2]}", color=c, lhead="cluster_splitters", label=d)
            elif "splitters" in a:
                g.edge(a, f"outputs-{outputs[len(outputs) // 2]}", color=c, lhead="cluster_outputs", label=d)
            else:
                g.edge(a, f"splitters-{splitters[len(splitters) // 2]}", color=c, lhead="cluster_splitters", label=d)
        else:
            # if "inputs" in a and "outputs" in b:
            #     g.edge(a, b, color=c, label=d, constraint='false')
            # else:
            g.edge(a, b, color=c, label=d)

    if debug:
        g.view()

    return base64.b64encode(g.pipe()).decode()


if __name__ == '__main__':
    print(get_img({'fibers': [{'box': 15,
                               'color': 'red',
                               'end_content_type': 11,
                               'end_object_id': 2,
                               'from_node': OrderedDict([('node_id', '8'),
                                                         ('node_type', 'inputs')]),
                               'id': 8,
                               'start_content_type': 12,
                               'start_object_id': 20,
                               'to_node': OrderedDict([('node_id', '9'),
                                                       ('node_type', 'outputs')])},
                              {'box': 15,
                               'color': 'red',
                               'end_content_type': 11,
                               'end_object_id': 2,
                               'from_node': OrderedDict([('node_id', '8'),
                                                         ('node_type', 'inputs')]),
                               'id': 9,
                               'start_content_type': 12,
                               'start_object_id': 20,
                               'to_node': OrderedDict([('node_id', '9'),
                                                       ('node_type', 'outputs')])},
                              {'box': 15,
                               'color': 'red',
                               'end_content_type': 11,
                               'end_object_id': 2,
                               'from_node': OrderedDict([('node_id', '8'),
                                                         ('node_type', 'inputs')]),
                               'id': 10,
                               'start_content_type': 12,
                               'start_object_id': 20,
                               'to_node': OrderedDict([('node_id', '9'),
                                                       ('node_type', 'outputs')])}],
                   'inputs': [{'box': 15, 'id': 20, 'input': 8, 'n_terminals': 8, 'node_id': '8'},
                              {'box': 15,
                               'id': 22,
                               'input': 9,
                               'n_terminals': 8,
                               'node_id': '9'}],
                   'outputs': [{'box': 15,
                                'id': 2,
                                'n_terminals': 8,
                                'node_id': '9',
                                'output': 9}],
                   'splitters': []}, debug=True))
