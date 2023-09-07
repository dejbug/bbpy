import wx
import wx.grid

class Grid:
    def __init__(self):
        self.cols = 0
        self.rows = 0


class CrossTablePane(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.font = wx.FFont(24, wx.SWISS)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, e):
        dc = wx.ClientDC(self)
        dc.SetFont(self.font)
        dc.DrawText('hello', 10, 10)


class PlayerPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style = wx.BORDER_SIMPLE)

        self.playerCount = 0
        self.maxColCount = 0
        self.showRankColumn = True
        self.backgroundColor = 'white'
        self.cells = None
        self.cross = None
        self.lastHoveredCell = None

        # self.SetBackgroundColour('steelblue')
        # self.SetBackgroundColour('#eee')
        self.SetBackgroundColour('black')

        self.font = wx.FFont(24, wx.SWISS)
        self.SetFont(self.font)

        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def InternalAddCell(self, cell):
        self.cells[cell.row][cell.col] = cell


    def AddCell(self, text, minWidth = 0, align = 0):
        minWidth *= self.font.GetPixelSize()[0]
        align = [wx.ALIGN_CENTRE_HORIZONTAL, wx.ALIGN_LEFT, wx.ALIGN_CENTRE_HORIZONTAL, wx.ALIGN_RIGHT][align]

        label = wx.StaticText(self, style = align | wx.ST_NO_AUTORESIZE)

        label.originalText = text

        label.col = self.colCount
        label.row = self.rowCount
        label.column = self.colCount - 1

        self.colCount += 1
        if self.colCount >= self.maxColCount:
            self.colCount = 0
            self.rowCount += 1
        self.InternalAddCell(label)

        label.SetLabelMarkup(text)
        label.SetBackgroundColour(self.backgroundColor)
        if minWidth: label.SetMinSize((minWidth, 0))
        label.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        # label.Bind(wx.EVT_LEFT_DOWN, self.OnMouseMotion)

        self.GetSizer().Add(label, 0, wx.EXPAND | wx.RESERVE_SPACE_EVEN_IF_HIDDEN)
        return label

    def RemoveAllCells(self):
        self.cells = None
        self.cross = None
        self.lastHoveredCell = None
        s = self.GetSizer()
        if s:
            s.Clear(delete_windows = True)
            self.SetSizer(None)

    def SetPlayerCount(self, count):
        self.RemoveAllCells()

        self.playerCount = count
        self.maxColCount = count + 3 + (1 if self.showRankColumn else 0)
        self.maxRowCount = count + 1

        self.cells = [
            [None for i in range(self.maxColCount)]
                for j in range(self.maxRowCount)]

        self.colCount = 0
        self.rowCount = 0

        sizer = wx.FlexGridSizer(count + 1, count + 4, 1, 1)
        sizer.AddGrowableCol(1)
        self.SetSizer(sizer)

        self.AddCell('#')
        self.AddCell('Name')
        for i in range(count):
            self.AddCell(f'<b>{i + 1}</b>')
        self.AddCell(' Pt ', 3)
        if self.showRankColumn:
            self.AddCell(' Pz ', 3)

        for i in range(count):
            self.AddCell(f'<b>{i + 1}</b>', 3)
            self.AddCell(' ', align = 1)
            for j in range(count):
                self.AddCell('x', 3)
            self.AddCell('0')
            if self.showRankColumn:
                self.AddCell('0')

    def GetCell(self, row, col):
        return self.cells[row][col]

    # def GetCellCoords(self, cell):
    #     return cell.row, cell.col

    def OnMouseMotion(self, e):
        cell = e.GetEventObject()
        if cell == self.lastHoveredCell: return
        self.lastHoveredCell = cell
        # find = self.GetCell(cell.row, cell.col)
        # print(cell.row, cell.col, cell == find, find.row, find.col)
        self.HighlightCross(cell.row, cell.col)

    def HighlightCross(self, row, col, color = "#dee"):
        if self.cross:
            left, top, mid = self.cross

            left.SetLabelMarkup(left.originalText)
            top.SetLabelMarkup(top.originalText)
            # mid.SetLabelMarkup(mid.originalText)

            left.SetBackgroundColour(self.backgroundColor)
            top.SetBackgroundColour(self.backgroundColor)
            mid.SetBackgroundColour(self.backgroundColor)

        left = self.cells[row][0]
        top = self.cells[0][col]
        mid = self.cells[row][col]

        left.SetLabelMarkup(f'<u>{left.originalText}</u>')
        top.SetLabelMarkup(f'<u>{top.originalText}</u>')
        # mid.SetLabelMarkup(f'<u>{mid.originalText}</u>')

        # left.SetLabelMarkup(f'<span color="red">{left.originalText}</span>')
        # top.SetLabelMarkup(f'<span color="red">{top.originalText}</span>')
        # mid.SetLabelMarkup(f'<span color="red">{mid.originalText}</span>')

        left.SetBackgroundColour(color)
        top.SetBackgroundColour(color)
        mid.SetBackgroundColour(color)
        self.cross = [left, top, mid]

    def OnMouseWheel(self, e):
        steps = e.GetWheelRotation() // e.GetWheelDelta()

        # self.font = wx.FFont(24, wx.SWISS)
        # self.SetFont(self.font)

        # print(dir(self.font))
        # print(self.font.GetPointSize())
        # print(self.font.GetPixelSize())

        if steps > 0:
            self.font = self.font.MakeLarger()
        else:
            self.font = self.font.MakeSmaller()
        self.SetFont(self.font)
        self.Freeze()
        self.SetPlayerCount(self.playerCount)
        self.Thaw()
        self.Refresh()



class MainFrame(wx.Frame):

    IDA_CLOSE = wx.NewIdRef()

    def __init__(self, parent = None):
        wx.Frame.__init__(self, parent, title = 'Hello', size = (1200, 800))

        # self.pane = CrossTablePane(self)
        self.pane = PlayerPanel(self)
        self.pane.SetPlayerCount(12)

        v = wx.BoxSizer(wx.VERTICAL)
        v.Add(self.pane, 0, wx.EXPAND | wx.ALL, 16)
        self.SetSizer(v)

        self.SetAcceleratorTable(wx.AcceleratorTable([
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, self.IDA_CLOSE),
        ]))

        self.Bind(wx.EVT_MENU, self.OnAccelClose, id = self.IDA_CLOSE)
        self.Show()

    def OnAccelClose(self, e):
        self.Close()


if __name__ == '__main__':
    a = wx.App(0)
    f = MainFrame()
    a.MainLoop()
