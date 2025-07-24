import requests
from bs4 import BeautifulSoup

# Trie Node definition
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

# Trie implementation
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        curr = self.root
        for ch in word:
            if ch not in curr.children:
                curr.children[ch] = TrieNode()
            curr = curr.children[ch]
        curr.is_end = True

    def search(self, word):
        curr = self.root
        for ch in word:
            if ch not in curr.children:
                return False
            curr = curr.children[ch]
        return curr.is_end

    def starts_with(self, prefix):
        curr = self.root
        for ch in prefix:
            if ch not in curr.children:
                return []
            curr = curr.children[ch]
        return self._collect_all_words(curr, prefix)

    def _collect_all_words(self, node, prefix):
        result = []
        if node.is_end:
            result.append(prefix)
        for ch, child in node.children.items():
            result += self._collect_all_words(child, prefix + ch)
        return result

# Edit distance (Levenshtein)
def edit_distance(s1, s2):
    dp = [[0]*(len(s2)+1) for _ in range(len(s1)+1)]
    for i in range(len(s1)+1):
        for j in range(len(s2)+1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    return dp[-1][-1]

# Suggest close word
def get_best_suggestion(word, word_list):
    best_word = None
    min_dist = float('inf')
    for w in word_list:
        dist = edit_distance(word, w)
        if dist < min_dist:
            min_dist = dist
            best_word = w
    return best_word if min_dist <= 2 else None

# Scrape definition
def fetch_definition(word):
    url = f"https://www.dictionary.com/browse/{word}"
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        meaning = soup.find("meta", {"name": "description"})
        if meaning and 'content' in meaning.attrs:
            return meaning['content']
        return "Definition not found."
    except Exception as e:
        return f"Error: {str(e)}"

# Load words from file
def load_words(filename):
    with open(filename) as f:
        return [line.strip().lower() for line in f if line.strip()]

# Main
def main():


    words = load_words("words.txt")
    trie = Trie()
    for word in words:
        trie.insert(word)

    while True:
        print("\n--- Word Lookup Dictionary ---")
        word = input("Enter a word (or 'exit' to quit): ").lower().strip()
        if word == "exit":
            break

        if trie.search(word):
            print(f"✅ '{word}' found in dictionary.")
            print("📖 Meaning:", fetch_definition(word))
        else:
            print(f"❌ '{word}' not found.")
            suggestion = get_best_suggestion(word, words)
            if suggestion:
                print(f"🔁 Did you mean: '{suggestion}'?")
                print("📖 Meaning:", fetch_definition(suggestion))
            else:
                print("⚠️ No suggestion found.")

        prefix = input("\nType a prefix to get suggestions (or press Enter to skip): ").strip()
        if prefix:
            print("🔍 Suggestions:", trie.starts_with(prefix))


if __name__ == "__main__":
    main()
