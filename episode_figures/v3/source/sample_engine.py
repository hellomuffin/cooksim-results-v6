"""Revision 3: execute wrong-ingredient substitution, plus in-motion frames."""
import copy,json,os,sys
from sample_engines import ROOT,COOK,revision,save_json
sys.path[:0]=[str(COOK),str(COOK/'tools')]
os.environ['COOKSIM_GRID']=str(COOK/'bench/v5/grid.json')
from exp_interact import build_episode
from cooksim.agents.highlevel import run_one,HighLevelController

def main():
    grid=json.loads((COOK/'bench/v5/grid.json').read_text())['grid']
    task=next(t for t in grid if t['cell']=='hard-nops / hard-map')
    _,r=build_episode(None,cell='hard_nops_hard_map',inject=True);g=r.game
    frames=[]
    def act(game,cmd,name,record=True):
        if cmd.startswith('go to the ') and 'nearest' not in cmd:cmd=cmd.replace('go to the ','go to the nearest ',1)
        before=copy.deepcopy(game.render_state());result=run_one(game,cmd)
        assert result['status']=='done',(cmd,result)
        if record:frames.append(dict(name=name,command=cmd,result=result,before=before,after=copy.deepcopy(game.render_state())))
    for i,cmd in enumerate(task['plan'][:28]):act(g,cmd,f'prep{i}',False)
    act(g,'go to the lettuce source','before_error')
    assert [i.name for i in g.cooks[0].holding.contents]==['fish']
    early=copy.deepcopy(g)
    act(early,'go to the fryer with the potato','redirect_chips')
    act(early,'scoop','correct_chips')
    act(early,'go to the serving pass','early_at_pass')
    act(early,'serve','early_served')
    assert early.stats['deliveries']==1
    act(g,'scoop','wrong_lettuce')
    assert [i.name for i in g.cooks[0].holding.contents]==['fish','lettuce']
    silent=copy.deepcopy(g);low=copy.deepcopy(g)
    act(silent,'go to the serving pass','silent_at_pass')
    act(silent,'serve','silent_rejected')
    assert silent.stats['failed_deliveries']==1
    for game,prefix in [(g,'high'),(low,'low')]:
        if prefix=='low':act(game,'wait 3',prefix+'_pause')
        for cmd,name in [('go to the trash','at_trash'),('trash','empty'),('go to the nearest empty counter','at_counter'),('put down','plate_down'),('go to the fish source','at_fish'),('pick up','fresh_fish')]:act(game,cmd,prefix+'_'+name)
        assert game.cooks[0].holding.name=='fish'
    save_json(ROOT/'candidates'/'revision3_fish.json',dict(kind='authored dialogue; engine-executed actions',engine_rev=revision(COOK),task='Fish & chips',cell=task['cell'],frames=frames,recipe=task['contents'],early_stats=early.stats,silent_stats=silent.stats,high_stats=g.stats,low_stats=low.stats,note='Lettuce substitutes for fried potato after plating cooked fish. Recovery excerpts end after discarding food and picking up a fresh fish, not a claim of complete recovery. No pre-error user speech.'))
    task=next(t for t in grid if t['cell']=='master-nops / hard-map')
    _,r=build_episode(None,cell='master_nops_hard_map',inject=True);g=r.game;nav=[]
    for i,cmd in enumerate(task['plan'][:15]):
        if cmd.startswith('go to the ') and 'nearest' not in cmd:cmd=cmd.replace('go to the ','go to the nearest ',1)
        ctrl=HighLevelController(g);assert ctrl.issue(cmd)
        j=0
        while ctrl.status=='running' and j<400:
            g.step([ctrl.step()]);j+=1
            if i in (2,6,10,14) and ctrl.status=='running':nav.append(dict(name=f'nav_{i:02d}_{j:02d}',command=cmd,after=copy.deepcopy(g.render_state())))
        assert ctrl.status=='done'
    save_json(ROOT/'candidates'/'revision3_nav.json',dict(engine_rev=revision(COOK),frames=nav))
    print('Verified three assistant alternatives and both recovery prefixes;',len(nav),'in-motion frames')

if __name__=='__main__':main()
