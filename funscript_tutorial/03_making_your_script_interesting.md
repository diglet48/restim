# Making your script interesting

If you are on this page, you have probably covered [create your first set of scripts](02_creating_your_first_set_of_scripts.md), and you have the [project snapshot](Sexy_Youtube_3.ofsp) that was shared at the end of that document.

For this step, I am sharing few python scripts that I wrote to automate parts of my workflow. They are using *funscript* class that I copied from @diglet's restim source code.

They are available zipped [here](tools.zip).

To use them you need python installed. Open a terminal in the unpacked folder (tools) and run:

`pip install -r .\requirements.txt`

First thing that I will do is spice up volume by making it *derivative* from our current volume (that I will rename to volume_ramp by clicking on Project -> Configure in OFS and then click on volume funscript and rename it to be filename.volume_ramp.funscript).

Now I do File -> Export -> Export all

I copy file *Sexy Youtube.beats.funscript* into tools folder (where I have the python scripts/terminal) and then first I run this command:

`python .\convert-to-speed.py '.\Sexy Youtube.beats.funscript' '.\Sexy Youtube.speed.funscript' 5`

This creates *Sexy Youtube.speed.funscript* which is 'derivate' (also in mathematical sense) of the beats funscript, meaning it shows the relative speed (the fastest part of file is 100, the slowest 0). The 5 is *window width*, meaning it calculates the average speed over 5 seconds. You might change this to have different responsiveness, i.e. increase it to make the speed change more slowly (but note that current speed will be average over *last* x seconds, so if you use too large window, like 20 sec, you might want to select and move all of the points of speed script to left by 10 seconds, so that current speed reflects the last 10 sec and next 10 sec).

I copy this file back to my work folder, I add it as existing to the project and after quick inspection I note that I have made "as fast as you can" section around 1h:03m way too fast, faster than any other part of the beats. That is why I want to reduce it to correspond roughly to the finisher section.

I am attaching a snapshot of project now, before I make manual changes to this speed axis: [project snapshot](Sexy_Youtube_4.ofsp)

I will use this speed axis to adjust the volume automatically, make it a bit higher where speed is fast, a bit lower where speed is slow. One caveat with this python script is that it only produces speed points where there are stroke points... so for "breaks" that have no points, the speed remains high if there was fast section before stop. I fix that by looking at heatmap of stroke and checking places that are black after red, removing one outlier point from speed script at end of breaks at 35:00, 43:18, 54:35, 1:05:21, 1:11:49, 1:14:08, 1:17:50. This is not so important in this case because all breaks have volume_ramp at 0, so adding few % to 0 won't do much, but it is important to be aware how the script works if you use it.

Now, what I can see is that speed of the beats in final section is not fastest, is slower than most of the edges/doubletime, and therefore the increase of volume will be less, so this will not be most intense sensation. As much as I love to make estim script that leaves you horny, I think in this one the final section would not be even very intense (if you already got through previous more intense parts). 
We could adjust this by increasing the speed of final section, but I don't want to use that, I want it to stay consistent with the stroke instructions and not have sudden increase on 'cum' because I personally love to try and ride & glide through that, experience orgasm but not be forced to ejaculate.
That is why I am going to make a small edit to volume_ramp now. I am selecting whole axis (ctrl+a while it is active) and then moving ALL of it 10 points down. I do that by holding shift and pressing down arrow 10 times. Now I still have same ramp, but I have some headroom to accommodate slower-than-max stroking speed in final minutes. 
I change the volume_ramp points at 1:24:38 (88->95), 1:24:57 (88-94) and 1:25:55 (90-100). I expect this will be what I want, but in case is not, we will repeat this adjustment and next steps few times until result is satisfactory.
I export the volume_ramp funscript, **and, don't forget to export the speed funscript** and I copy both to tools folder.
Then I run these two commands:
`python .\combine-funscripts.py '.\Sexy Youtube.volume_ramp.funscript' '.\Sexy Youtube.speed.funscript' '.\Sexy Youtube.volume.funscript' 8`

`python .\combine-funscripts.py '.\Sexy Youtube.volume_ramp.funscript' '.\Sexy Youtube.speed.funscript' '.\Sexy Youtube.volume_foc.funscript' 6`

This takes volume_ramp and combines it with speed funscript, using ratio of 8 - meaning 8/9 of result is from ramp and 1/9 of weight is from speed. That gives interesting variation, makes the intensity vary with speed automatically, and if we get feedback that it is too much/too low, we can easily regenerate volume funscript from our building blocks.

I also created volume_foc that has more intense speed-based ramps, 1/6th instead of 1/8th, and that is because foc-based stim devices seem to have more dynamic range and sensations don't get too intense too quickly with volume changes, I am using 1/6 as a provisional value for now, it might change based on testing and feedback.

Ok, now for volume (and volume_foc) I usually do Special Functions -> Simplify (Ramer-Douglas-Pecker) with value of about 0.25, just to remove all the extra points that are not needed, and export the funscripts.

Here is [project snapshot](Sexy_Youtube_5.ofsp) in current condition. This should now already be decent experience.

We are not, however, using any of the more advanced axes in restim (pulse parameters). I am not sure I want to write what exactly I do there, because these are very individual, I would not want everyone to try to mimic what I do, I'd rather have more diversity, but based on how we got volume, I am sure you are getting ideas how you can easily combine existing building blocks in different ratios to modify pulse frequency, width, rise time etc. For example I like to make rise time inverse of speed, but maybe you will move all points down or up, or compress/expand range etc.

I might write more parts to discuss that after I receive feedback for what has been done already.


