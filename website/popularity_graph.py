import numpy as np
import matplotlib.pyplot as plt
    

def get_song_pop(playlist):
    stats = {}
    for song in playlist['items']:
        song  = song['track']
        stats[song['name']] = song['popularity']
    return stats

def graph_pop_songs(stats):
        company=list(stats.keys())
        revenue=list(stats.values())

        fig=plt.figure()
        
        ax= plt.subplot()

        xpos=np.arange(len(company))

        bars = plt.bar(xpos,revenue)


        annot = ax.annotate("", xy=(5,0), xytext=(-20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="black", ec="b", lw=2),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(bar):
            x = round(bar.get_x()+bar.get_width())
            y = bar.get_y()+bar.get_height()
            annot.xy=(x,y)
            x = company[x]
        

            text = (x,y)
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.4)
        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                for bar in bars:
                    cont, ind = bar.contains(event)
                    if cont:
                        update_annot(bar)
                        annot.set_visible(True)
                        fig.canvas.draw_idle()
                        return
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

        plt.show()
        
