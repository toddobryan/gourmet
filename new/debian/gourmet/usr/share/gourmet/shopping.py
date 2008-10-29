import convert, sys
from gettext import gettext as _

class shopper:
    def __init__ (self, inglist):
        """We expect a list of tuples/lists, each of which contains
        amount, unit, key [[amt,un,key],[amt,un,key],...]"""
        ## First, we create a dictionary from our list (keyed by ingredient)
        ## each value in the dict. is a list of values. We'll try to add these
        ## as best as we can.
        self.dic = {}
        self.default_pantry=[_('flour, all purpose'),_('sugar'),_('salt'),
                             _('black pepper, ground'),
                             _('ice'), _('water'),
                             _('oil, vegetable'),
                             _('oil, olive')]
        self.init_pantry()
        self.mypantry = {}
        for a,u,k in inglist:
            if self.pantry.has_key(k) and self.pantry[k]:
                #print "%s is in pantry" %k
                dic=self.mypantry
            else:
                dic=self.dic
            try:
                a = float(a)
            except:
                a = None
            if dic.has_key(k):
                dic[k].append([a,u])
            else:
                dic[k]=[[a,u]]
        self.init_converter()
        for ing,amts in self.dic.items():
            self.dic[ing]=self.combine_ingredient(ing,amts)
        for ing,amts in self.mypantry.items():
            self.mypantry[ing]=self.combine_ingredient(ing,amts)        
        self.init_orgdic()
        self.init_ingorder_dic()
        self.init_catorder_dic()

    def init_converter (self):
        self.cnv = convert.converter()

    def combine_ingredient (self, ing, amts):
        """We take an ingredient and a list of amounts. We return a
        list of amounts (ideally shortened, if combinifying is
        possible)."""
        itms = []
        for a,u in amts:
            if not itms:
                ## if this is our first...
                itms.append([a,u])
            else:
                flag = 0
                ind = 0
                while not flag and len(itms) > ind:
                    i = itms[ind]
                    add= self.cnv.add_reasonably(i[0],i[1],a,u,ing)
                    ## add_reasonably returns a nice a,u pair if successful
                    if add:
                        itms.pop(ind) # out with the old...
                        itms.append(add) # in with the new
                        flag = 1
                    else:
                        ind += 1
                if not flag:
                    itms.append([a,u])
        return itms

    def ing_to_string (self, ing, amts):
        return "%s %s" %(self.amt_to_string(amts),ing)

    def amt_to_string (self, amts):
        retstr = self.cnv.amt_string(amts[0])
        if len(amts) > 1:
            for a in amts[1:]:
                retstr = "%s + %s" %(self.cnv.amt_string(a), retstr)
        return retstr

    def pretty_print (self, out=sys.stdout):
        self.list_writer(
            write_category= lambda c: out.write("\n---\n%s\n---\n"%c),
            write_item = lambda a,i: out.write("%s %s\n"%(a,i))
            )

    def list_writer (self,
                      write_category,
                      write_item,):
        org = self.organize(self.dic)
        for c,d in org:
            write_category(c)
            for i,a in d:
                write_item(a,i)

    def organize (self, dic=None):
        """We organize our ingredients into lists in the form.
           [Category, [[ingredient, amt],
                       [ingredient, amt]...
                      ]
           ]"""
        ## first we build a dictionary, since it gives us an
        ## easy way to sort by category
        cats = {}
        if not dic:
            pass
        for i,a in dic.items():
            if self.orgdic.has_key(i):
                c = self.orgdic[i]
            else:
                c = _("Unknown")
            if cats.has_key(c):
                cats[c][i]=a
            else:
                cats[c]={i:a}
        ## next we turn our nested dictionaries into nested lists
        lst = []
        for c,d in cats.items():
            itms = []
            for i,amts in d.items():
                itms.append([i,self.amt_to_string(amts)])
            lst.append([c,itms])
        ## now that we have lists, we can sort them
        lst.sort(self._cat_compare)
        for l in lst:
            l[1].sort(self._ing_compare)
        return lst

    def _cat_compare (self,cata,catb):
        """Put two categories in order"""
        cata = cata[0]
        catb = catb[0]
        if self.catorder_dic.has_key(cata) and self.catorder_dic.has_key(catb):
            # if both categories have known positions, we use them to compare
            cata = self.catorder_dic[cata]
            catb = self.catorder_dic[catb]
        else:
            # otherwise, we just use > to sort alphabetically
            cata = cata.lower()
            catb = catb.lower()
        if cata > catb: return 1
        if cata == catb: return 0
        else: return -1

    def _ing_compare (self,inga,ingb):
        """Put two ingredients in order"""
        inga = inga[0]
        ingb = ingb[0]
        if self.ingorder_dic.has_key(inga) and self.ingorder_dic.has_key(ingb):
            # if both ings have known positions, we use them to compare
            inga = self.ingorder_dic[inga]
            ingb = self.ingorder_dic[ingb]
        else:
            # otherwise, we just use > to sort alphabetically
            inga = inga.lower()
            ingb = ingb.lower()
        if inga > ingb: return 1
        if inga == ingb: return 0
        else: return -1


    def get_porg_categories (self):
        """Return a list of categories used for sorting."""
        tmp = {}
        for v in self.orgdic.values():
            tmp[v]=1
        return tmp.keys()

    def add_org_itm (self, itm, cat):
        self.orgdic[itm]=cat
        #for k,v in self.orgdic.items():
            #print "%s:%s, "%(k,v)
            
    def add_to_pantry (self, key):
        self.pantry[key]=True

    def remove_from_pantry (self, key):
        self.pantry[key]=False
    
    def init_orgdic (self):
        """This allows those subclassing us to do something fancy... 
        as is, we just use a default dictionary."""
        self.default_orgdic = setup_default_orgdic()
        self.orgdic = self.default_orgdic

    def init_ingorder_dic (self):
        self.ingorder_dic = {}
    def init_catorder_dic (self):
        debug("Initializing empty catorder_dic",5)
        self.catorder_dic = {}

    def init_pantry (self):
        self.pantry={}
        for i in self.default_pantry:
            self.pantry[i]=True
            
    def get_orgcats (self):
        """Return a list of categories being used for our shopper"""
        self.orgcats=[]
        for v in self.orgdic.values():
            if v and (v not in  self.orgcats):
                self.orgcats.append(v)
        self.orgcats.sort()
        return self.orgcats

def setup_default_orgdic ():
    from defaults import lang as defaults
    return defaults.shopdic