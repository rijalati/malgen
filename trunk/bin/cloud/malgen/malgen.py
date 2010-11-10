from __future__ import division
__copyright__ = """
Copyright (C) 2008 - 2009  Open Data ("Open Data" refers to
one or more of the following companies: Open Data Partners LLC,
Open Data Research LLC, or Open Data Technologies LLC.)

This is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

from optparse import OptionParser, make_option
import cPickle as cp
import random, bisect
import os
from math import *
import time
import sys
import subprocess
import datetime

NSECONDSPERYEAR       = 31536000.0
NSECONDSPERDAY        = 60.*60.*24
REPORTFREQ            = 10000000

FIXEDWIDTH            = True
ELEMENTPADLENGTH      = 19
STRICT                = False


class WeightedRandomPermutationArray(object):
  def __init__(self, items):
    self.items   = []
    self.weights = []
    total        = sum(y for x,y in items.iteritems())
    count        = 0
    for it,weight in items.iteritems():
      count += weight
      self.items.append(it)
      self.weights.append(count)
    self.total = total-1

  def __call__(self):
    rank  = int(random.random() * self.total)
    index = bisect.bisect(self.weights, rank)
    n=self.items[index]
    return self.items[index]


class RecordGenerator(object):
  def __init__(self, out = None, power = -1.0, scale = 0.0):
    self.nseconds    = 0.0   # number of seconds in run.
    self.pComp       = 0.0   # compromise probability
    self.delay       = 0.0   # delay between compromise and tag
    self.gen         = random.Random()
    self.power       = power # parameter of power law
    self.inPower     = 1.0/(1.0-self.power)
    self.scale       = scale # scale number of hits from power law
    self.eventsPerEntity = 0.0
    if out is not None:
      self.out          = file(out,'w')
    else:
      self.out          = sys.stdout
    self.entities       = {}
    self.entitiesUsed   = {}

  def iterateSites(self, startidx, nrecords, hosthash, nBGcompromisedSites, distfile=None):
    i = 0
    hashstr               = str( hosthash)
    starttime = lasttime  = time.time()
    ntot                  = 0
    calcThreshhold        = float(len(self.entities)) / 100.0
    toRemove              = {}
    self.compdate         = {}
    self.weightedEntities = WeightedRandomPermutationArray(self.entities)
    self.nsitesGenerated  = 0
    lastcomp              = starttime-NSECONDSPERYEAR
    REPORTFREQ            = int(0.1 * nrecords)
    
    while ( ntot < nrecords ):
        if len(toRemove) >= calcThreshhold:
          for entity, k in toRemove.iteritems():
            del self.entities[entity]
          self.weightedEntities = WeightedRandomPermutationArray(self.entities)
          needsRecalc = 0
          toRemove    = {}
        n=int((self.scale/5.0)*(1-self.power)*self.gen.uniform(0,1)**(-1*self.inPower))
        self.siteid+=1
        self.nsitesGenerated+=1
        siteID = str(self.siteid)
        compsite = 0
        if (self.siteid <= self.nCompromisedSites and self.siteid>0):
          compsite = 1
          thiscomp = starttime - random.uniform(0.9999,1.0)*(starttime-lastcomp)
          self.compdate[siteID] =datetime.datetime.fromtimestamp(thiscomp)
          lastcomp = max(lastcomp,thiscomp)
        for id in range(0,n):
          cFlag = '0'
          if (i%REPORTFREQ)==0:
            newtime = time.time()
            print "%i Events Generated "%i
            lasttime = newtime
          # Generate a random entity and a date between now and a year ago:
          entity           = self.weightedEntities()
          time_interval    = random.random() * NSECONDSPERYEAR
          date = datetime.datetime.fromtimestamp( starttime - time_interval )
          if (entity in self.compentities) and (date > self.taggedentities[entity]):
            # previously infected
            cFlag = '1'
          elif compsite == 1:
            meanPriorVisits  = (time_interval/self.nseconds) * self.eventsPerEntity/self.nCompromisedSites
            prior_correction = 1.0 - ((1.0 - self.pComp)**(max(0.,meanPriorVisits - 1.0)))
            if self.gen.random() < self.pComp + prior_correction - self.pComp*prior_correction:
              if (date > self.compdate[siteID]):
                if ((entity not in self.uncmpentities) or
                (date > self.uncmpentities[entity])):
                  # entity subject to compromise
                  cFlag = '1'
                  try:
                    self.compentities[entity] = min(date,self.compentities[entity])
                    self.taggedentities[entity] = self.compentities[entity]+datetime.timedelta(0,self.delay) # 1 days later
                  except:
                    self.compentities[entity] = date
                    self.taggedentities[entity] = self.compentities[entity]+datetime.timedelta(0,self.delay) # 1 days later
                else:
                  pass # predates known time when uncompromised
            else:
                try:
                  self.uncmpentities[entity] = max(date,self.uncmpentities[entity])
                except:
                  self.uncmpentities[entity] = date
          else:
            pass # not a compromise vector or predates its identity as one.
          self.entitiesUsed.setdefault(entity,0)
          self.entities[entity]-= 1
          if (self.entities[entity] <= 0):
            toRemove[entity] = 1
          if abs(int(siteID)-self.uniqid) >= nBGcompromisedSites:
            if FIXEDWIDTH:
                # 11 is the number of bytes left to reach 100
                evntid = ( str(i+startidx).zfill(11) + hashstr.zfill(ELEMENTPADLENGTH + 1) )
                datestr = str(date)
                if len(datestr)== 19:
                    datestr += '.000000'
                outrecord = '|'.join([evntid, datestr, siteID.zfill(ELEMENTPADLENGTH),
                    cFlag,  entity.zfill(ELEMENTPADLENGTH) ])
            else:
                evntid = ( str(i+startidx) +  hashstr)
                outrecord = '|'.join([evntid,str(date),siteID,cFlag,entity])

            ntot+=1
            if STRICT:
                if ntot <= nrecords:
                    self.out.write(outrecord+'\n')
                else:
                    break
            else:
                self.out.write(outrecord+'\n')

            l = len(outrecord)
            try:
              self.reclength[l] += 1
            except:
              self.reclength = {l:1}

          i+=1

class RecordPrepare(RecordGenerator):
  """ 
  Generate events and a list of sites where the number
  of events for each site is distributed
  according to a power law, f(x) dx = x^-n dx.
  The events are associated with entities
  entities. The number of events per entity is
  generated randomly from a Gaussian distribution
  with a mean provided by a user. Entities may
  have been compromised by visits to a previously
  identified set of sites and have been tagged with
  this information at some time interval following the
  compromise. This information is included in the
  event records for all sites.
  """
  def __init__(self, outdir, outfile, hosthash):

    RecordGenerator.__init__(self)

    INITIALIZATIONFILE = file(outdir + '/INITIAL.txt','rb')
    if (os.path.exists(INITIALIZATIONFILE.name)):
      comment_line_1           = cp.load(INITIALIZATIONFILE)
      comment_line_2           = cp.load(INITIALIZATIONFILE)
      comment_line_3           = cp.load(INITIALIZATIONFILE)
      comment_line_4           = cp.load(INITIALIZATIONFILE)
      comment_line_5           = cp.load(INITIALIZATIONFILE)
      comment_line_6           = cp.load(INITIALIZATIONFILE)
      self.nrec_unseeded_blocks= cp.load(INITIALIZATIONFILE)
      self.power               = cp.load(INITIALIZATIONFILE)
      self.scale               = cp.load(INITIALIZATIONFILE)
      self.delay               = cp.load(INITIALIZATIONFILE)
      self.out                 = cp.load(INITIALIZATIONFILE)
      self.compentities        = cp.load(INITIALIZATIONFILE)
      self.uncmpentities       = cp.load(INITIALIZATIONFILE)
      self.taggedentities      = cp.load(INITIALIZATIONFILE)
      self.siteid              = cp.load(INITIALIZATIONFILE)
      self.nCompromisedSites   = cp.load(INITIALIZATIONFILE)
      self.entities            = cp.load(INITIALIZATIONFILE)
      self.weightedEntities    = cp.load(INITIALIZATIONFILE)
      self.uniqid              = startidx*10000000 + hosthash
      self.siteid              = self.uniqid + self.siteid
    INITIALIZATIONFILE.close()

    self.out = file('/'.join([outdir,outfile]), 'w')

  def iterateSites(self, startidx, hosthash, distfile=None):

    RecordGenerator.iterateSites(self, startidx, self.nrec_unseeded_blocks,hosthash, 0, distfile)

    outdir      = os.path.dirname(self.out.name)
    METADATAFILE=file(outdir + '/METADATA.txt','w')
    METADATAFILE.write('Number of Sites %i\n'%self.nsitesGenerated)
    METADATAFILE.write('Number of Entities used %i\n'%len(self.entitiesUsed))
    METADATAFILE.write('Requested number of Compromised Sites %i\n'%self.nCompromisedSites)
    METADATAFILE.write('Infection Probability %f\n'%self.pComp)
    METADATAFILE.write('Delay to Identifying compromised Entity: %f\n'%(self.delay/NSECONDSPERDAY))
    METADATAFILE.write('Record Length Distribution:\n')
    for i, d in self.reclength.items():
      METADATAFILE.write('%i %i \n'%(i,d))
    METADATAFILE.close()    

    self.out.close()

class CompromisedRecordPrepare(RecordGenerator):
  """
  Generate events for compromised sites.
  """
  def __init__(self, power, nrecords, nblocks, nrec_unseeded_blocks, pComp, delay, out, ndays, eventsPerEntity, stdEventsPerEntity,bg ,local, scale):

    RecordGenerator.__init__(self, out, power, scale)

    REPORTFREQ = int(0.1*nrecords)

    self.siteid           = 0
    self.uniqid           = 0
    self.pComp            = float(pComp)
    self.nseconds         = NSECONDSPERDAY * ndays
    self.delay            = NSECONDSPERDAY * float(delay)
    self.eventsPerEntity  = float(eventsPerEntity)
    meanHits              = float(eventsPerEntity) * float(ndays)
    stdHits               = float(stdEventsPerEntity) * float(meanHits)
    self.compentities     = {}
    self.uncmpentities    = {}
    self.taggedentities   = {}

    count  = 0
    visits = 0

    # number of compromised siites includes 'virtual' sites
    # which can compromise entities external to our known list.
    self.nCompromisedSites = int(bg)+int(local)
    self.bg = int(bg)   
    while (visits< (nrecords + nblocks*nrec_unseeded_blocks)):
      if (len(self.entities)%REPORTFREQ)==0:
         print "%i Entity"%len(self.entities)
      n = int(self.gen.gauss(meanHits,stdHits))
      entity = str(count + 1).zfill(12)
      self.entities[entity] = n
      visits+=n
      count+=1
    self.nrec_unseeded_blocks = nrec_unseeded_blocks

  def iterateSites(self, startidx, nrecords, hosthash, distfile=None):

    RecordGenerator.iterateSites(self, startidx, nrecords, hosthash, self.bg, distfile)

    # Generate information which is needed by any subsequent uncompromised
    # runs.
    outdir = os.path.dirname(self.out.name)
    INITIALIZATIONFILE = file(outdir + '/INITIAL.txt','wb')
    cp.dump("Comments about the data run -----/",INITIALIZATIONFILE)
    cp.dump("Total # Blocks: " + str(nblocks),INITIALIZATIONFILE)
    cp.dump("Block Size: " + str(nrec_unseeded_blocks),INITIALIZATIONFILE)
    cp.dump("Initial Block Size: " + str(nrecords),INITIALIZATIONFILE)
    cp.dump("Strict: " + str(STRICT),INITIALIZATIONFILE)
    cp.dump("-----/ End comments",INITIALIZATIONFILE)
    cp.dump(self.nrec_unseeded_blocks,INITIALIZATIONFILE)
    cp.dump(self.power,INITIALIZATIONFILE)
    cp.dump(self.scale,INITIALIZATIONFILE)
    cp.dump(self.delay,INITIALIZATIONFILE)
    cp.dump(self.out.name,INITIALIZATIONFILE)
    cp.dump(self.compentities,INITIALIZATIONFILE)
    cp.dump(self.uncmpentities,INITIALIZATIONFILE)
    cp.dump(self.taggedentities,INITIALIZATIONFILE)
    cp.dump(self.siteid,INITIALIZATIONFILE)    
    cp.dump(self.nCompromisedSites, INITIALIZATIONFILE)
    cp.dump(self.entities, INITIALIZATIONFILE)
    cp.dump(self.weightedEntities,INITIALIZATIONFILE)
    INITIALIZATIONFILE.close()

    METADATAFILE = file(outdir + '/METADATA.txt','w')
    METADATAFILE.write('Number of Sites %i\n'%self.siteid)
    METADATAFILE.write('Number of Compromised Sites %i\n'%min(self.siteid,self.nCompromisedSites))
    METADATAFILE.write('Requested number of Compromised Sites %i\n'%self.nCompromisedSites)
    METADATAFILE.write('BG-Local Compromise Ratio %f\n'%(float(self.bg)/float(self.nCompromisedSites)))
    METADATAFILE.write('Number of Entities used %i\n'%len(self.entitiesUsed))
    METADATAFILE.write('Infection Probability %f\n'%self.pComp)
    METADATAFILE.write('Delay to Identifying compromised Entity: %f\n'%(self.delay/NSECONDSPERDAY))
    METADATAFILE.write('Record Length Distribution:\n')
    for i, d in self.reclength.items():
      METADATAFILE.write('%i %i \n'%(i,d))
    METADATAFILE.write('Compromised Dates\n')
    for i,d in self.compdate.items():
      METADATAFILE.write( '%s %s \n'%(i,d))
    METADATAFILE.close()    

    self.out.close()
      
if __name__=="__main__":

  usemsg = "\n \t \t Use nonzero seed_index for non-seed runs. \n \
           For seed runs, the arguments correspond to: \n \
           number of events seed run, \n \
           number of events per non-seed run, and \n \
           total number of non-seed runs, respectively."
  
  usage = "usage: \n \
           Seed Run- \n \
           %prog [options] 0 nrecs nrecsperblock blocks  \n \
           All other runs- \n \
           %prog [options] seed_index \n "+usemsg

  misuse = "usage: \n \
           Seed Run- \n \
           malgen.py [options] 0 nrecs nrecsperblock blocks\n \
           All other runs- \n \
           malgen.py [options] seed_index \n "+usemsg

  version = "%prog 0.9"
  options = [
    make_option('-p','--pComp',default=0.7, 
                help="Compromise Probability (default .70)"),
    make_option('-P','--power',default=-3.5, 
                help="Power for events per site distribution (default -3.5)"),
    make_option('-d','--delay',default=1.0, 
                help="Delay in days in tagging compromise (default 1.0)"),
    make_option('-D','--ndays',default=365,
                help="Number of days for data sample (default 365)"),
    make_option('-m','--events_per_entity',default=27.0,
                help="Mean number of events per day per entity (default 27)"),
    make_option('-s','--std_events_per_entity',default=.1,
                help="Std Deviation in number of events per day per entity \
as a fraction of the mean number of events per day (default .1)"),
    make_option('-O','--outdir',default='/tmp/',
                help="Directory for output and for seed initialization data (default /tmp/)"),
    make_option('-o','--outfile',default='events-malstone.dat',
                help="Output filename (default events-malstone.dat)"),
    make_option('-g','--background',default=0,
                help="Number of background sites that contribute to external compromises (default 0)"),
    make_option('-l','--local',default=1000,
                help="Number of sites acting as source of compromise (default 1000)"),
    make_option('-S','--sitescale',default=10000,
                help="Scale factor determining typical number of events per site (default 10000)"),
    make_option('-t','--truncate',default=False, action="store_true",
                help="Truncate the generated records so that exactly the \
specified number of records is generated rather than following the statistical distribution (default False)")
  ]
  parser = OptionParser(usage=usage, version=version, option_list=options)
  (options, arguments) = parser.parse_args()

  try:      
    startidx = int(arguments[0])
  except:
    msg="At least one argument (specifying event id start) is required."
    print("%s\n"%msg)
    print("%s \n"%misuse)
    sys.exit(1)

  # There are two ways to uses malgen.  If you are benchmarking algorithms which
  # process the data, you are probably only concerned with how many records are
  # generated.
  # If you are performing analytics on the data, the statisctical distribution
  # of the dataa is probably more important.
  # Which of these to use is controlled by the -t, --truncate flag.
  #   1. Generate the data following the distribution but generate exactly the
  #   specified number of records
  #   2. Generate the data following the distribution, the number of records
  #   generate may exceed the specified number (around the order of 1/100
  #   percent).  This is the default behavior.
  STRICT = options.truncate

  # event ID field needs to be unique across all data files, so use a hash
  # of the host name to append to IDs to ensure uniqueness.
  hosthash = hash( subprocess.Popen(["hostname"],
                                    stdout=subprocess.PIPE).communicate()[0] )

  if startidx != 0:
    sitesSetup=RecordPrepare(options.outdir, options.outfile, hosthash)
    u=sitesSetup.iterateSites(startidx, hosthash)
  else:
    try:
      nrecords = int(arguments[1])
    except:
      msg= 'Using start_index of 0 implies a seed run for which \n \
 you must specify the number of records in the seed block \n \
 for the data set as the second argument.'
      print("%s\n"%msg)
      sys.exit(1)
    try:
      nrec_unseeded_blocks = int(arguments[2])
    except:
      msg= 'Using start_index of 0 implies a seed run for which \n \
 you must also specify the number of events for each block \n \
 that will be used for all non-seed blocks as the third argument.'
      print("%s\n"%msg)
      sys.exit(1)
    try:
      nblocks = int(arguments[3])
    except:
      msg= '  Using start_index of 0 implies a seed run for which \n \
 you must specify the  number of non-seed blocks \n \
 for the data set as the fourth argument.'
      print("%s\n"%msg)
      sys.exit(1)
    sitesSetup=CompromisedRecordPrepare(options.power,
                                        nrecords, nblocks,
                                        nrec_unseeded_blocks, 
                                        options.pComp,
                                        options.delay,
                                        options.outdir+options.outfile,
                                        options.ndays,
                                        options.events_per_entity,
                                        options.std_events_per_entity,
                                        options.background,
                                        options.local,
                                        options.sitescale)
    u=sitesSetup.iterateSites(startidx, nrecords, hosthash)

