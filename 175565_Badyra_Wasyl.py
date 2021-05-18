from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
from math import *

# udało się zaimplementować algorytm który generuję płaszczyznę w 3d na podstawie punktów przestrzennych
# realizuję to w kilku iteracjacj (generuję nowe punkty, dodaję do moich punktów i wywołuję funkcję ponownie)
# dla odpowienio dużego radius1 funkcja wykonuje się w 1 itercacji
# nie udało się zaanimować wyrównywania siatki płaszczyzny


def generate_points_from_mat(x_data, y_data, z_data, x, y, z):
    not_found_x = []
    not_found_y = []
    found_x = []
    found_y = []
    found_z = []
    # dla każdego punktu musimy wyliczyć wartość, korzystam z interpolacji IDW
    # link do wikipedii https://en.wikipedia.org/wiki/Inverse_distance_weighting
    for i in range(0, len(x)):
        for k in range(0, len(y)):
            importance = 0
            value = 0
            for j in range(0, len(x_data)):
                # dla każdego punktu w promieniu obliczam wartość z metody IDW
                distance = sqrt(pow(x[i] - x_data[j], 2) + pow(y[k] - y_data[j], 2))
                if distance < radius1:
                    weight = 1 / pow(distance, p1)
                    value = z_data[j] * weight + value
                    importance = importance + weight
            # gdy dany punkt nie miał w swoim otoczeniu rzadnego innego punktu to zapisuję mu tymczasowo wartość 0
            # oraz jego współrzędne zapisuję do list, aby potem poszukiwać dla tych punktów wartości aż lista nie będzie
            # pusta
            if importance == 0 or value == 0:
                z[i, k] = 0
                not_found_x.append(i)
                not_found_y.append(k)
            # gdy punkt ma jakąś wartość, to kopiuję współrzędne punktu oraz wartość którą muszę mu przypisać,
            # przypisania dokonuję po wykonaniu pętli
            else:
                found_x.append(i)
                found_y.append(k)
                found_z.append(value / importance)

    # ważne, aby przypisać punkty po ich poszukiwaniu, gdy przypisywałem je od razu w głównej pętli, to otrzymywałem za
    # duże wartości, dlatego zapisuję w listach dane punktów i uzupełniam z_cords po pętli
    # (punkt dopiero co znaleziony był uwzględniany przy obliczaniu wartości jego sąsiada)
    for i in range(0, len(found_x)):
        z_cords[found_x[i], found_y[i]] = found_z[i]
    # zwracam współrzędne punktów, których wartości nie zostały jeszcze wyznaczone
    return not_found_x, not_found_y


def generate_points_until_all_found(x_data, y_data, z_data, list_x, list_y):
    # teraz w pętli while będę poszukiwał wartości punktów dopóki dla każdego nie przypiszę jakiejś wartości
    # ilość wywołań pętli zależy od radius2, czyli od wartości określającej w jakiej bliskości musi być jakiś inny
    # punkt, aby punktowi bez wartości można było przypisać wartość
    while len(list_x) != 0:
        # gdy punktowi przypiszę wartość muszę go usunąć z listy punktów do poszukiwania
        elements_found = []
        found_z = []
        for i in range(0, len(list_x)):
            importance = 0
            value = 0
            for j in range(0, len(x_data)):
                for k in range(0, len(y_data)):
                    distance = sqrt(
                        pow(x_data[list_x[i]] - x_data[j], 2) + pow(y_data[list_y[i]] - y_data[k], 2))
                    if distance < radius2 and distance != 0:
                        weight = 1 / pow(distance, p2)
                        value = z_cords[j, k] * weight + value
                        importance = importance + weight
            # gdy dany punkt nie miał w swoim otoczeniu rzadnego innego punktu to zapisuję mu tymczasowo wartość 0
            if importance == 0 or value == 0:
                z_data[list_x[i], list_y[i]] = 0
            # gdy punkt ma jakąś wartość, to kopiuję współrzędne punktu oraz wartość którą muszę mu przypisać,
            # przypisania dokonuję po wykonaniu pętli
            else:
                elements_found.append(i)
                found_z.append(value / importance)
        # od końca moich list przypisuję wartości do z_data i usuwam z listy punktów współrzędne już znalezionych
        # punktów
        for i in range(len(elements_found) - 1, -1, -1):
            z_data[list_x[elements_found[i]], list_y[elements_found[i]]] = found_z[i]
            list_x.pop(elements_found[i])
            list_y.pop(elements_found[i])

# ilość punktów dla osi x i y
size = 50
# odległość w jakiej będziemy odczytywać punkty dla generowania punktów dla danych z pliku mat
radius1 = 0.01
# współczynnik określający jak duży wpływ ma odległość między punktami na wagę jaką przypiszemy wartości punktu
# przy pierwszej generacji
p1 = 1
# odległość w jakiej będziemy generować punkty na podstawie wcześniej wygenerowanych punktów z pliku mat
radius2 = 0.03
# współczynnik określający jak duży wpływ ma odległość między punktami na wagę jaką przypiszemy wartości punktu
# przy drugiej generacji
p2 = 1

dict_data = loadmat('data_map.mat')
dict_data.keys()

x_data = dict_data['data_map'][:, 0]
y_data = dict_data['data_map'][:, 1]
z_data = dict_data['data_map'][:, 2]

# trzeba wygenerować siatkę punktów na podstawie których będziemy potem interpolować wartości na podstawie znanych punktów
x_cords = np.linspace(np.min(x_data), np.max(x_data), size)
y_cords = np.linspace(np.min(y_data), np.max(y_data), size)
z_cords = np.zeros(shape=(len(x_cords), len(y_cords)))

point_x, point_y = generate_points_from_mat(x_data, y_data, z_data, x_cords, y_cords, z_cords)
generate_points_until_all_found(x_cords, y_cords, z_cords, point_x, point_y)

x_axis, y_axis = np.meshgrid(x_cords, y_cords)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x_axis, y_axis, z_cords)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

