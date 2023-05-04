from typing import List

class Solution:
    def findMaximizedCapital(k , w ,p , c):
        n = len(p)
        is_used = [False]*n
        print(is_used)
        result = w
        project_index = 0 
        while project_index < k :
            print("="*100)
            less_than_list = []
            print(f"Current value of w : that is capital is : {w}")
            for i in range(n) :
                if w >= c[i] and is_used[i] == False: 
                    less_than_val = (i , p[i] , c[i])
                    print(f"Less than val : {less_than_val}")
                    less_than_list.append(less_than_val)
            print(f"The full less than list : {less_than_list}")
            curr_max_profit = float("-inf")
            curr_max_index = None
            curr_max_capital = float("-inf")
            for index , profit , capital in less_than_list :
                if profit > curr_max_profit : 
                    curr_max_profit = profit
                    curr_max_index = index
                    curr_max_capital = capital
            result += curr_max_profit
            w = curr_max_profit
            
            is_used[curr_max_index] = True
            project_index += 1
            print("="*100)

        return result
            
k = 2
w = 0 
p = [1,2,3]
c = [0,1,1]

# print(Solution.findMaximizedCapital(k, w, p, c))
a =  [[0]*5 for _ in range(10) ] 
a[0][1] = 10
a[0][0] = 23
print(a)


from typing import List

class Solution:

    def inside(self , i , j , grid) :
        if i in range(len(grid)) and j in range(len(grid[0])) : 
            return True
        return False
    
    def bfs(self , i , j, grid , visited ) : 
        if not self.inside(i , j , grid) : 
            return -1
        if visited[i][j] : 
            return "vis"
        if grid[i][j] == "N" :
            visited[i][j] = True
            return -1
        if grid[i][j] == "H" : 
            visited[i][j] = True
            top = self.bfs(i-1 , j , grid , visited)
            bottom = self.bfs(i+1 , j , grid , visited )
            left = self.bfs(i , j-1 , grid , visited )
            right = self.bfs(i , j +1 , grid , visited)
            if top == bottom == left == right == -1 : 
                return -1
            else : 
                possible_list = []
                if top != -1 or top != "vis": 
                    possible_list.append(top)
                    
                if bottom != -1 or bottom !=  "vis" : 
                    possible_list.append(bottom)
                    
                if left != -1 or left != "vis" : 
                    possible_list.append(left)
                    
                if right != -1 or right != "vis" : 
                    possible_list.append(right)
                
                return 1 + min(possible_list)    
        if grid[i][j] == "W": 
            return 0
            
                
    def chefAndWells(self, n : int, m : int, grid : List[List[str]]) -> List[List[int]]:
        ans = [ [0]*m for _ in range(n)]
        visited = [[False for _ in range(m)] for _ in range(n)]
        for i in range(n) : 
            for j in  range(m) : 
                symbol = grid[i][j]
                if symbol ==  "N" : 
                    ans[i][j] = -1
                    continue
                if symbol == "W" : 
                    continue
                if symbol == "H" : 
                    distance = 2* self.bfs(i , j , grid , visited)
                    ans[i][j] = distance
                    print(ans)
        return ans
        