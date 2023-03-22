#!/usr/bin/env python
# coding: utf-8
import json
import math

from amcat4py import AmcatClient

from tools import get_amcatclient, upload_batches, check_index, get_argument_parser, setup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import pandas as pd
import numpy as np


INDEX = "quantum"
FIELDS = dict(
    speakers='tag',
    videoid='keyword',
    title='text',
    url='url',
    place='keyword',
    year='long',
    number='long',
    transcript="text",
    nquantum="long",
    topic_quantum="keyword",
    holistic="long",
    technology2="long",
    laser="long",
    mri="long",
    smartphone="long",
    qnetwork="long",
    qsensor="long",
    spooky="long",
    spooky_quote='keyword',
    economic="long",
    economic_sentence='keyword',
    benefits="long",
    benefits_sentence='keyword',
    progress="long",
    progress_quote='keyword',
    b_life="long",
    b_finance="long",
    b_logistics="long",
    b_security="long",
    b_defense="long",
    b_energy="long",
    b_argiculture="long",
    risks="long",
    risks_quote='keyword',
    r_life="long",
    r_finance="long",
    r_logistics="long",
    r_security="long",
    r_defense="long",
    r_energy="long",
    r_argiculture="long",
    superposition="long",
    explain_superposition="long",
    quote_superposition='keyword',
    entanglement="long",
    explain_entanglement="long",
    quote_entanglement='keyword',
    explain_contextuality="long",
    quote_contextuality='keyword'

)
conn = AmcatClient("http://localhost/amcat")
conn.delete_index(INDEX)
conn.create_index(INDEX)
conn.set_fields(INDEX, FIELDS)
df = pd.read_excel(r'~/Dropbox/quantum/data/All_data_1.xlsx', sheet_name = 'List_data')

frames = pd.read_excel(r'~/Dropbox/quantum/data/All_data_2.xlsx', sheet_name='Content')

def get_frames(videoid):
    for f in (frames.to_dict('records')):
        if f['VideoID'] == videoid:
            aspects = dict(
                videoid=videoid,
                topic_quantum=f['topic_quantum'],
                holistic=f['holistic'],
                technology2=f['technology2'],
                laser=f['laser'],
                mri=f['mri'],
                smartphone=f['smartphone'],
                computer=f['computer'],
                nuclear=f['nuclear'],
                qcomputer=f['qcomputer'],
                qnetwork=f['qnetwork'],
                qsensor=f['qsensor'],
                spooky=f['spooky'],
                spooky_quote=f['spooky_quote'],
                economic=f['economic'],
                economic_sentence=f['economic_sentence'],
                benefits=f['benefits'],
                benefits_sentence=f['benefits_sentence'],
                progress=f['progress'],
                progress_quote=f['progress_quote'],
                b_life=f['b_life'],
                b_finance=f['b_finance'],
                b_logistics=f['b_logistics'],
                b_security=f['b_security'],
                b_defense=f['b_defense'],
                b_energy=f['b_energy'],
                b_argiculture=f['b_argiculture'],
                risks=f['risks'],
                risks_quote=f['risks_quote'],
                r_life=f['r_life'],
                r_finance=f['r_finance'],
                r_logistics=f['r_logistics'],
                r_security=f['r_security'],
                r_defense=f['r_defense'],
                r_energy=f['r_energy'],
                r_argiculture=f['r_argiculture'],
                superposition=f['superposition'],
                explain_superposition=f['explain_superposition'],
                quote_superposition=f['quote_superposition'],
                entanglement=f['entanglement'],
                explain_entanglement=f['explain_entanglement'],
                quote_entanglement=f['quote_entanglement'],
                explain_contextuality=f['explain_contextuality'],
                quote_contextuality=f['quote_contextuality']
            )
            return(aspects)


for i, row in enumerate(df.to_dict('records')):
    videoid = row['VideoID']
    url = f"https://www.youtube.com/watch?v={videoid}"
    print(i, videoid)
    speaker = row['Speaker']
    speaker2 = row['Speaker2']
    if isinstance(speaker2, str):
        speakers = [speaker, speaker2]
    else:
        speakers = [speaker]
    year = row['Year']
    texts = YouTubeTranscriptApi.get_transcript(videoid)
    text = []
    for t in texts:
        phrase = t['text']
        text.append(phrase)
    text = "\n".join(text)
    frames2 = get_frames(videoid)
    topic_quantum = frames2['topic_quantum']
    holistic = frames2['holistic']
    technology2 = frames2['technology2']
    laser = frames2['laser']
    if np.isnan(laser):
        laser = 0
    mri = frames2['mri']
    if not (mri):
        mri = 0
    smartphone = frames2['smartphone']
    computer = frames2['computer']
    nuclear = frames2['nuclear']
    qcomputer = frames2['qcomputer']
    if np.isnan(qcomputer):
        qcomputer = 0
    qnetwork = frames2['qnetwork']
    qsensor = frames2['qsensor']
    spooky = int(frames2['spooky'])
    print(f"SPOOKY is {spooky}")
    spooky_quote = frames2['spooky_quote']
    economic = frames2['economic']
    economic_sentence = frames2['economic_sentence']
    benefits = frames2['benefits']
    benefits_sentence = frames2['benefits_sentence']
    progress = frames2['progress']
    progress_quote = frames2['progress_quote']
    b_life = frames2['b_life']
    b_finance = frames2['b_finance']
    b_logistics = frames2['b_logistics']
    b_security = frames2['b_security']
    b_defense = frames2['b_defense']
    b_energy = frames2['b_energy']
    b_argiculture = frames2['b_argiculture']
    risks = frames2['risks']
    risks_quote = frames2['risks_quote']
    r_life = frames2['r_life']
    r_finance = frames2['r_finance']
    r_logistics = frames2['r_logistics']
    r_security = frames2['r_security']
    r_defense = frames2['r_defense']
    r_energy = frames2['r_energy']
    r_argiculture = frames2['r_argiculture']
    superposition = frames2['superposition']
    explain_superposition = frames2['explain_superposition']
    quote_superposition = frames2['quote_superposition']
    entanglement = frames2['entanglement']
    explain_entanglement = frames2['explain_entanglement']
    quote_entanglement = frames2['quote_entanglement']
    explain_contextuality = frames2['explain_contextuality']
    quote_contextuality = frames2['quote_contextuality']
    a = dict(
        text=text,
        title=row['Title'],
        url = url,
        date=f"{year}-01-01",
        videoid=videoid,
        place=row['Place'],
        number=row['Number'],
        nquantum=row['nquantum'],
        speakers=speakers,
        topic_quantum=topic_quantum,
        holistic=holistic,
        technology2=technology2,
        laser=laser,
        mri=mri,
        smartphone=smartphone,
        computer=computer,
        nuclear=nuclear,
        qcomputer=qcomputer,
        qnetwork=qnetwork,
        qsensor=qsensor,
        spooky=int(spooky),
        spooky_quote=spooky_quote,
        economic=economic,
        economic_sentence=economic_sentence,
        benefits=benefits,
        benefits_sentence=benefits_sentence,
        progress=progress,
        progress_quote=progress_quote,
        b_life=b_life,
        b_finance=b_finance,
        b_logistics=b_logistics,
        b_security=b_security,
        b_defense=b_defense,
        b_energy=b_energy,
        b_argiculture=b_argiculture,
        risks=risks,
        risks_quote=risks_quote,
        r_life=r_life,
        r_finance=r_finance,
        r_logistics=r_logistics,
        r_security=r_security,
        r_defense=r_defense,
        r_energy=r_energy,
        r_argiculture=r_argiculture,
        superposition=superposition,
        explain_superposition=explain_superposition,
        quote_superposition=quote_superposition,
        entanglement=entanglement,
        explain_entanglement=explain_entanglement,
        quote_entanglement=quote_entanglement,
        explain_contextuality=explain_contextuality,
        quote_contextuality=quote_contextuality

    )
    a = {k:v for (k,v) in a.items() if v !="" and v != " "}
    print(json.dumps(a, indent=2))
    upload_batches(conn, INDEX, [a], "youtube", "TEDex", chunk_size=1)
