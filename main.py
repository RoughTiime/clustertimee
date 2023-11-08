import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
import functools
from numbers import Integral
from scipy.sparse import issparse
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import _safe_indexing, check_random_state, check_X_y
from sklearn.utils._param_validation import (
    Interval,
    StrOptions,
    validate_params,
)
from sklearn.metrics.pairwise import _VALID_METRICS, pairwise_distances, pairwise_distances_chunked
import random
import csv
import math
import statistics as stat
from streamlit_option_menu import option_menu

st.title(f"Welcome,")
#opsi 1
selected = option_menu(
    menu_title=None,
    # options=["Home","Generate Random","Upload CSV File","How to Use"],
    options=["Home","How to Use"],
    icons=["house-fill","info-circle-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#eee"},
        "icon": {"color": "black", "font-size": "18px"}, 
        "nav-link": {"font-size": "20px", "text-align": "center", "margin":"4px", "--hover-color": "#00000"},
        "nav-link-selected": {"background-color": "grey"},
    }
)


if selected == "Home" :
            uploaded_file = st.file_uploader(label="Upload your CSV File", type='csv')

            global df
            global numeric_columns

            if uploaded_file is not None:
                print("no file uploaded")
                try:
                    df = pd.read_csv(uploaded_file)
                    numeric_columns=list(df.select_dtypes(['float','int']).columns)
                    chart_select = st.selectbox(
                        label="Preview File",
                        options=['','Scatterplots', 'Table']
                )

                    if chart_select == 'Scatterplots' :
                        st.subheader("Scatterplot Settings")
                        try:
                            x_values = st.selectbox('X axis', options=numeric_columns)
                            y_values = st.selectbox('Y axis', options=numeric_columns)
                            plot = px.scatter(data_frame=df, x=x_values, y=y_values)
                            st.plotly_chart(plot) #display chart
                            print(x_values)
                        except Exception as e:
                            print(e)
                            print("err--------------------------")

                    if chart_select == 'Table' :
                        st.write(df)
                except Exception as e:
                    print(e)
            st.markdown("<p style='text-align: center; color: black;'>Or</p>", unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
            randoms = col3.button("Generate Random",key=123)
            if randoms:
                    # number=st.text_input("Insert number of User ", key=int)
                    number = st.slider('How old are you?', 0, 10, 4,step=2)
                    jumlah_sample = int(number)
                    print(jumlah_sample)
                    def rand():
                    #return(random.randint(-10,10))
                        return(random.uniform(-10, 10))

                    header = ['x', 'y']
                    data = []
                    for i in range(jumlah_sample):
                        data.append([rand(), rand()])

                    with open('test.csv', 'w', encoding='UTF8', newline='') as f:
                        writer = csv.writer(f)

                        # write the header
                        writer.writerow(header)

                        # write multiple rows
                        writer.writerows(data)
            df = pd.read_csv('test.csv')
            jumlah_sample = len(df. index)
            plot = px.scatter(data_frame=df, x=df['x'], y=df['y'])
            st.plotly_chart(plot)
            plt.scatter(df['x'], df['y'])
            plt.scatter(0,0,marker='^',color='black',s=500)
            plt.xlabel('x')
            plt.ylabel('y')

            raw = df.values.tolist()
            colors = []
            for i in range(jumlah_sample):
                hexadecimal = "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])
                colors.append(hexadecimal)
            
            def check_number_of_labels(n_labels, n_samples):
                if not 1 < n_labels < n_samples:
                    raise ValueError(
                        "Number of labels is %d. Valid values are 2 to n_samples - 1 (inclusive)"
                        % n_labels
                    )

            def silhouette_score(
                X, labels, *, metric="euclidean", sample_size=None, random_state=None, **kwds
            ):
                if sample_size is not None:
                    X, labels = check_X_y(X, labels, accept_sparse=["csc", "csr"])
                    random_state = check_random_state(random_state)
                    indices = random_state.permutation(X.shape[0])[:sample_size]
                    if metric == "precomputed":
                        X, labels = X[indices].T[indices].T, labels[indices]
                    else:
                        X, labels = X[indices], labels[indices]
                return np.mean(silhouette_samples(X, labels, metric=metric, **kwds))


            def _silhouette_reduce(D_chunk, start, labels, label_freqs):
                n_chunk_samples = D_chunk.shape[0]
                # accumulate distances from each sample to each cluster
                cluster_distances = np.zeros(
                    (n_chunk_samples, len(label_freqs)), dtype=D_chunk.dtype
                )

                if issparse(D_chunk):
                    if D_chunk.format != "csr":
                        raise TypeError(
                            "Expected CSR matrix. Please pass sparse matrix in CSR format."
                        )
                    for i in range(n_chunk_samples):
                        indptr = D_chunk.indptr
                        indices = D_chunk.indices[indptr[i] : indptr[i + 1]]
                        sample_weights = D_chunk.data[indptr[i] : indptr[i + 1]]
                        sample_labels = np.take(labels, indices)
                        weights= [[] for i in range(len(label_freqs))]
                        for k in range(len(label_freqs)):
                            for l in range(len(sample_weights)):
                                if k == sample_labels[l]:
                                    weights[k].append(sample_weights[l])
                        c = ''
                        for x in range(len(sample_weights)):
                            if sample_weights[x]==0:
                                c = sample_labels[x]
                        for y in range(len(weights)):
                            if c == y and len(weights[y]) > 1:
                                weights[y].remove(0)
                            weights[y] = min(weights[y])
                        cluster_distances[i] += weights
                else:
                    for i in range(n_chunk_samples):
                        sample_weights = D_chunk[i]
                        sample_labels = labels
                        weights= [[] for i in range(len(label_freqs))]
                        for k in range(len(label_freqs)):
                            for l in range(len(sample_weights)):
                             if k == sample_labels[l]:
                                weights[k].append(sample_weights[l])
                        c = ''
                        for x in range(len(sample_weights)):
                            if sample_weights[x]==0:
                             c = sample_labels[x]
                        for y in range(len(weights)):
                            if len(weights[y]) == 1:
                             weights[y] = 0
                            elif c == y and len(weights[y]) > 1:
                                weights[y].remove(0)
                                weights[y] = max(weights[y])
                            else:
                                weights[y] = min(weights[y])
                        cluster_distances[i] += weights

                # intra_index selects intra-cluster distances within cluster_distances
                end = start + n_chunk_samples
                intra_index = (np.arange(n_chunk_samples), labels[start:end])
                # intra_cluster_distances are averaged over cluster size outside this function
                intra_cluster_distances = cluster_distances[intra_index]
                # of the remaining distances we normalise and extract the minimum
                cluster_distances[intra_index] = np.inf
                inter_cluster_distances = cluster_distances.min(axis=1)
                return intra_cluster_distances, inter_cluster_distances

            def silhouette_samples(X, labels, *, metric="euclidean", **kwds):
                X, labels = check_X_y(X, labels, accept_sparse=["csr"])

                # Check for non-zero diagonal entries in precomputed distance matrix
                if metric == "precomputed":
                    error_msg = ValueError(
                        "The precomputed distance matrix contains non-zero "
                        "elements on the diagonal. Use np.fill_diagonal(X, 0)."
                    )
                    if X.dtype.kind == "f":
                        atol = np.finfo(X.dtype).eps * 100
                        if np.any(np.abs(X.diagonal()) > atol):
                            raise error_msg
                    elif np.any(X.diagonal() != 0):  # integral dtype
                        raise error_msg

                le = LabelEncoder()
                labels = le.fit_transform(labels)
                n_samples = len(labels)
                label_freqs = np.bincount(labels)
                check_number_of_labels(len(le.classes_), n_samples)

                kwds["metric"] = metric
                reduce_func = functools.partial(
                    _silhouette_reduce, labels=labels, label_freqs=label_freqs
                )
                results = zip(*pairwise_distances_chunked(X, reduce_func=reduce_func, **kwds))
                intra_clust_dists, inter_clust_dists = results
                intra_clust_dists = np.concatenate(intra_clust_dists)
                inter_clust_dists = np.concatenate(inter_clust_dists)

                sil_samples = inter_clust_dists - intra_clust_dists
                with np.errstate(divide="ignore", invalid="ignore"):
                    sil_samples /= np.maximum(intra_clust_dists, inter_clust_dists)
                # nan values are for clusters of size 1, and should be 0
                return np.nan_to_num(sil_samples)

            k = []
            k2 = []
            for i in range(2,jumlah_sample):
                kmeans_model = KMeans(n_clusters=i).fit(df)
                labels = kmeans_model.labels_
                k.append(metrics.silhouette_score(df, labels, metric='euclidean'))
                k2.append(silhouette_score(df, labels, metric='euclidean'))

            score = max(k)
            n = k.index(score)+2

            score2 = max(k2)
            n2 = k2.index(score2)+2

            # KMeans
            print('jumlah klaster yang terbentuk oleh silhouette versi asli: ', n)
            print('jumlah klaster yang terbentuk oleh silhouette modifikasi: ', n2)

            km = KMeans(n_clusters=n)

            y_predicted = km.fit_predict(df)

            df['kelompokCluster'] = y_predicted

            km2 = KMeans(n_clusters=n2)

            z_predicted = km2.fit_predict(df)

            df['kelompokClusterMod'] = z_predicted

            plt.subplots(figsize=(15, 5))
            for i in range(2):
                plt.subplot(1, 2, i+1)
                n = n if i == 0 else n2
                for j in range(n):
                    dfi = df[df.kelompokCluster==j] if i == 0 else df[df.kelompokClusterMod==j]
                    plt.scatter(dfi.x,dfi['y'],color=colors[j])

            plt.xlabel('x')
            plt.ylabel('y')

            plt.scatter(0,0,marker='^',color='black',s=500)
            plt.grid()
            
            trad = raw
            trad2 = [] # add radius + sorted
            trad3 = [] # paired
            trad4 = [] # formatted

            for e in trad:
                radius = np.linalg.norm(np.array((e[0],e[1])))
                trad2.append([e[0], e[1], radius.item()])

            def based_on_radius(e):
                return e[2]

            trad2.sort(key=based_on_radius)

            for i in range(int(math.ceil(len(trad2)/2))):
                trad3.append([trad2[i],trad2[-i-1]])

            for i in range(len(trad3)):
                trad3[i][0].append(i)
                trad3[i][1].append(i)
                #print(trad3[i])
                trad4.append(trad3[i][0])
                trad4.append(trad3[i][1])

            trad_final = pd.DataFrame(trad4, columns = ['x','y','radius','kelompokCluster'])

            for i in range(int(jumlah_sample/2)):
                dfti = trad_final[trad_final.kelompokCluster==i]
                plt.scatter(dfti.x,dfti['y'],color=colors[i])

            plt.xlabel('x')
            plt.ylabel('y')

            plt.scatter(0,0,marker='^',color='black',s=500)
            plt.grid()
            eta = 4
            N = 10**4
            o = 0.1
            st.write(jumlah_sample)
            st.write(len(trad4))
            st.write(len(df. index))
            for i in range(jumlah_sample):
                for j in range(jumlah_sample):
                    if df.iloc[i].x == trad4[j][0] and df.iloc[i].y == trad4[j][1] :
                        trad4[j].append(df.iloc[i].kelompokCluster)
                        trad4[j].append(df.iloc[i].kelompokClusterMod)

            rndm = np.random.randn(1,10000)
            for e in trad4:
                re = np.random.randn(1,N)
                im = np.random.randn(1,N)
                h = []
                g = []
                for i in range(N):
                    res = math.sqrt(e[2]**(-eta))*(complex(re[0][i],im[0][i]))/math.sqrt(2)
                    h.append(res)
                    gain = abs(res)**2
                    g.append(gain)
                e.append(h)
                e.append(g)

            SNR = range(50)
            snr = []
            for i in SNR:
                pow = 10**(i/10)
                snr.append(pow)     
                                                  
            clstr = [] # for silhouette
            for i in range(n2):
                clstr_n = []
                for u in trad4:
                    if int(u[5]) == i:
                        clstr_n.append(u)
                clstr_n.sort(key=based_on_radius)
                clstr.append(clstr_n)

            clstrd = [] # for hybrid
            for i in range(n):
                clstr_n = []
                for u in trad4:
                    if int(u[4]) == i:
                        clstr_n.append(u)
                clstr_n.sort(key=based_on_radius)
                clstrd.append(clstr_n)

            k_means = []

            for i in snr:
                datarates = []
                for j in clstr:
                    a = [9*10**(-i) for i in range(1,len(j)+1)]
                    b = a + [0]
                    for k in range(len(j)):
                        p = jumlah_sample*i/n
                        # math.log2(1 + a*p*)
                        datarate = [] # setiap gain / user
                        gain = j[k][-1]
                        for g in gain:
                            datarate.append(math.log2(1 + g*a[-k-1]*p/(sum(b[-k-1:])*p*g + o**2)))
                        datarates.append(stat.mean(datarate))
                    k_means.append(stat.mean(datarates)/n2)
            
            n = 0
            mod = []
            for k in clstrd: # iterasi tiap klaster
                for i in range(int(math.ceil(len(k)/2))): # iterasi setiap user di klaster yg lg di cek
                    mod.append([k[i], k[-i-1]])
            modified = []

            for i in snr:
                datarates = []
                for c in mod:
                    datarate = []
                    datarate2 = []
                    if c[0] == c[1]:
                        gain = c[0][-1]
                        for g in gain:
                            datarate.append(math.log2(1 + g*i))
                        datarates.append(stat.mean(datarate))
                else:
                    gain = c[0][-1]
                    gain2 = c[1][-1]
                    for g in gain:
                        datarate.append(math.log2(1 + 0.09*g*i))
                    for g in gain2:
                        datarate2.append(math.log2(1 + (0.9*g*i)/(0.09*g*i + o**2)))
                    datarates.append(stat.mean(datarate))
                    datarates.append(stat.mean(datarate2))
                modified.append(stat.mean(datarates)/len(mod))

            traditional = []

            for i in snr:
                datarates = []
                for u in trad4:
                    datarate = [] # setiap gain / user
                    gain = u[-1]
                    if trad4.index(u) % 2 == 0: # near
                        for g in gain:
                            datarate.append(math.log2(1 + 0.18*g*i))
                        datarates.append(stat.mean(datarate))
                    elif trad4.index(u) % 2 == 1: # far
                        for g in gain:
                            datarate.append(math.log2(1 + (1.8*g*i)/(0.18*g*i + o**2)))
                        datarates.append(stat.mean(datarate))
                traditional.append(stat.mean(datarates)/12)

            TDMA = []
            # print(pd.DataFrame(trad4, columns = ['x','y','radius','kelompokCluster','kmeansCluster','h','g']))
            for i in snr:
                datarates = [] # setiap user
                for u in trad4:
                    datarate = [] # setiap gain / user
                    gain = u[-1]
                    for g in gain:
                        datarate.append(math.log2(1 + g*i))
                    datarates.append(stat.mean(datarate))
                TDMA.append(stat.mean(datarates)/jumlah_sample)

            # print(pd.DataFrame(trad4, columns = ['x','y','radius','kelompokCluster','kmeansCluster']))
            plt.plot(np.array(k_means), color='green') # modified 2: silhouette modified
            plt.plot(np.array(modified), color='yellow') # modified 1: hybrid
            plt.plot(np.array(traditional), color='blue')
            plt.plot(np.array(TDMA), color='red')
            plt.xlabel('SNR (dB)')
            plt.ylabel('Sum-rate (bps/Hz)')
            plt.legend(['Modified 2','Modified 1','Conventional','TDMA'])
            

if selected == "How to Use" :
     st.title(f"wdwdwedwew")
#hide humburger and watermark
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#hide link button 
st.markdown("""
    <style>
    /* Hide the link button */
    .stApp a:first-child {
        display: none;
    }
    
    .css-15zrgzn {display: none}
    .css-eczf16 {display: none}
    .css-jn99sy {display: none}
    </style>
    """, unsafe_allow_html=True)
