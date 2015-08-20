class formatCoord:
    def __init__(self,X):
        self.X = X
        self.numrows,self.numcols=self.X.shape[0:2]
        
    def update_coord(self, x, y):
        col = int(x+0.5)
        row = int(y+0.5)
        if col>=0 and col<self.numcols and row>=0 and row<self.numrows:
            z = self.X[row,col]
            try:
                return 'x=%1.4f, y=%1.4f, z=%s '%(x, y, ' '.join(map(str,z)))
            except TypeError:
                return 'x=%1.4f, y=%1.4f, z=%s '%(x, y, z)
        else:
            return 'x=%1.4f, y=%1.4f'%(x, y)
