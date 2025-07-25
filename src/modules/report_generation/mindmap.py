
class MindMap:
    def insert(self, current_node, new_node):
        # idk yet
        self.clean()
    
    def clean(self):
        for node in bfs(self.root):
            if node.num_children() > K:
                self.reorganize(node)
    
    def reorganize(self, node):
        new_subtopics = self.lm.generate_subtopics(node)
        old_children = node.childen
        node.children = []
        node.children = new_subtopics
        mapping = map_old_children_to_subtopics(old_children, new_subtopics)

        for old_child, subtopic in mapping:
            self.insert(subtopic, old_child)

        # TODO: delete concepts with no supporting information and collapse concepts with only one subtopic