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

print(Solution.findMaximizedCapital(k, w, p, c))
