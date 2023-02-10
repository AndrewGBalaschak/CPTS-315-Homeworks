//Code (c) Andrew Balaschak, 2023
//idk why you'd want to steal this though because it probably should have been done in Python

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>
#include <iterator>
using namespace std;

//global support threshold
const int support = 100;

/********************************************************************************
** STRUCTS
********************************************************************************/

struct itemCount{
    string item;
    int count;
};

struct itemPair{
    string item1;
    string item2;
    int count;
    double confidence1to2;
    double confidence2to1;
};

bool operator==(const itemPair& l, const itemPair& r){
    return (l.item1 == r.item1 && l.item2 == r.item2) || (l.item1 == r.item2 && l.item2 == r.item1);
}

bool compareConfidencePair(const itemPair &l, const itemPair &r){
    if(max(l.confidence1to2, l.confidence2to1) == max(r.confidence1to2, r.confidence2to1)){
        if(l.item1.compare(r.item1) == 0){
            if(l.item2.compare(r.item2) < 0){
                return true;
            }
            else{
                return false;
            }
        }
        else if(l.item1.compare(r.item1) < 0){
            return true;
        }
        else{
            return false;
        }
    }
    return max(l.confidence1to2, l.confidence2to1) > max(r.confidence1to2, r.confidence2to1);
}

struct itemTriple{
    string item1;
    string item2;
    string item3;
    int count;
    double confidence12to3;
    double confidence13to2;
    double confidence23to1;
};

bool compareConfidenceTriple(const itemTriple &l, const itemTriple &r){
    if(max(l.confidence12to3, max(l.confidence13to2, l.confidence23to1)) > max(r.confidence12to3, max(r.confidence13to2, r.confidence23to1))){
        if(l.item1.compare(r.item1) == 0){
            if(l.item2.compare(r.item2) == 0){
                if(l.item3.compare(r.item3) < 0){
                return true;
                }
                else{
                    return false;
                }
            }
            if(l.item2.compare(r.item2) < 0){
                return true;
            }
            else{
                return false;
            }
        }
        else if(l.item1.compare(r.item1) < 0){
            return true;
        }
        else{
            return false;
        }
    }



    return max(l.confidence12to3, max(l.confidence13to2, l.confidence23to1)) > max(r.confidence12to3, max(r.confidence13to2, r.confidence23to1));
}

bool operator==(const itemTriple& l, const itemTriple& r){
    return
    (l.item1 == r.item1 && l.item2 == r.item2 && l.item3 == r.item3) ||
    (l.item1 == r.item1 && l.item2 == r.item3 && l.item3 == r.item2) ||
    (l.item1 == r.item2 && l.item2 == r.item1 && l.item3 == r.item3) ||
    (l.item1 == r.item2 && l.item2 == r.item3 && l.item3 == r.item1) ||
    (l.item1 == r.item3 && l.item2 == r.item1 && l.item3 == r.item2) ||
    (l.item1 == r.item3 && l.item2 == r.item2 && l.item3 == r.item1);
}

/********************************************************************************
** FUNCTIONS
********************************************************************************/

//reads in browsing data from filename
//returns 2D vector
vector<vector<string>> readData(string filename){
    ifstream datafile;
    datafile.open(filename);

    //declaring 2d vector for strings
    //[i] = user
    //[j] = item
    vector<vector<string>> output;

    string line;
    while(getline(datafile, line)){
        string temp_string;
        vector<string> temp_vector;

        //create a stream for tokenizing
        stringstream stream(line);

        //add each entry to a vector
        while(getline(stream, temp_string, ' ')){
            temp_vector.push_back(temp_string);
        }

        //add the vector we made to the main database vector
        output.push_back(temp_vector);
        temp_vector.clear();
    }
    datafile.close();
    return output;
}

//debug function
//prints 2D vector of strings
void print2DVector(vector<vector<string>> vect){
    for(int i = 0; i < vect.size(); i++){
        for(int j = 0; j < vect[i].size(); j++){
            cout << vect[i][j] << " ";
        }
        cout << endl;
    }
}

//counts the number of occurences of each item in the dataset
//returns a vector of itemCount structs
vector<itemCount> countItems(vector<vector<string>> vect){
    vector<itemCount> output;

    //stores item IDs that have already been counted
    vector<string> checked;
    
    for(int i = 0; i < vect.size(); i++){
        for(int j = 0; j < vect[i].size(); j++){
            string item = vect[i][j];
            //if the item has not been counted yet
            if(find(checked.begin(), checked.end(), item) == checked.end()){
                int item_count = 0;

                //sum the count of the item in each row
                for(int k = i; k < vect.size(); k++){
                    item_count += count(vect[k].begin(), vect[k].end(), item);
                }

                //mark the item as checked
                checked.push_back(item);

                //add the item and its count to the output
                struct itemCount temp_struct = {item, item_count};
                output.push_back(temp_struct);
            }
        }
    }
    return output;
}

//returns true if item is a frequent item
bool isFrequentItem(vector<string> frequent_items, string item){
    if(find(frequent_items.begin(), frequent_items.end(), item) != frequent_items.end()){
        return true;
    }
    return false;
}

//returns a vector of itemPair structs wherein both items are frequent
vector<itemPair> getPairs(vector<vector<string>> vect, vector<string> frequent_items){
    vector<itemPair> output;

    for(int i = 0; i < vect.size(); i++){
        for(int j = 0; j < vect[i].size()-1; j++){

            //check if item is frequent
            if(isFrequentItem(frequent_items, vect[i][j])){

                //check each other item in user's history
                for(int k = j+1; k < vect[i].size(); k++){
                    
                    //check if second item is frequent
                    if(isFrequentItem(frequent_items, vect[i][k])){

                        //create a pairing for the items
                        struct itemPair temp_pair = {vect[i][j], vect[i][k], 1};

                        //search for item pairing in output
                        vector<itemPair>::iterator it = find(output.begin(), output.end(), temp_pair);

                        //if pair is not already in output, add it to the output
                        if(it == output.end()){
                            output.push_back(temp_pair);
                        }

                        //otherwise, add 1 to their count
                        else{
                            it->count++;
                        }
                    }  
                }
            }
        }
    }
    return output;
}

//returns a vector of itrmTriple structs wherein both pairs are frequent
vector<itemTriple> getTriples(vector<string> frequent_items, vector<itemPair> frequent_pairs){
    vector<itemTriple> output;
    
    for(int i = 0; i < frequent_pairs.size(); i++){
        for(int j = 0; j < frequent_pairs.size(); j++){
            struct itemTriple temp_triple;

            //if the pairs share an item, create a triple for the items
            if(frequent_pairs[i].item1 == frequent_pairs[j].item1){
                temp_triple = {frequent_pairs[i].item1, frequent_pairs[i].item2, frequent_pairs[j].item2, 1};
            }
            else if(frequent_pairs[i].item1 == frequent_pairs[j].item2){
                temp_triple = {frequent_pairs[i].item1, frequent_pairs[i].item2, frequent_pairs[j].item1, 1};
            }
            else if(frequent_pairs[i].item2 == frequent_pairs[j].item1){
                temp_triple = {frequent_pairs[i].item1, frequent_pairs[i].item2, frequent_pairs[j].item2, 1};
            }
            else if(frequent_pairs[i].item2 == frequent_pairs[j].item2){
                temp_triple = {frequent_pairs[i].item1, frequent_pairs[i].item2, frequent_pairs[j].item1, 1};
            }

            //search for item triple in output
            vector<itemTriple>::iterator it = find(output.begin(), output.end(), temp_triple);

            //if triple is not already in output, add it to the output
            if(it == output.end()){
                output.push_back(temp_triple);
            }

            //otherwise, add 1 to their count
            else{
                it->count++;
            }
        }
    }
    return output;
}

int main(){
    //declaring 2d vector for strings
    //[i] = user
    //[j] = item
    vector<vector<string>> data;

    data = readData("browsing-data.txt");
    //print2DVector(data);

    /********************************************************************************
    ** FREQUENT ITEMS
    ********************************************************************************/
    //count occurence of each item
    vector<itemCount> item_count = countItems(data);

    //filter to items that are frequent
    vector<string> frequent_items;
    for(int i = 0; i < item_count.size(); i++){
        if(item_count[i].count >= support){
            frequent_items.push_back(item_count[i].item);
        }
    }

    /********************************************************************************
    ** ITEM PAIRS
    ********************************************************************************/
    //identifying pairs of frequent items and their count
    vector<itemPair> item_pairs = getPairs(data, frequent_items);

    //filter to pairs that are frequent
    vector<itemPair> frequent_pairs;
    for(int i = 0; i < item_pairs.size(); i++){
        if(item_pairs[i].count >= support){
            frequent_pairs.push_back(item_pairs[i]);
        }
    }

    //compute confidence scores
    for(int i = 0; i < frequent_pairs.size(); i++){
        int item1_count, item2_count;

        for(int j = 0; j < item_count.size(); j++){
            if(item_count[j].item == frequent_pairs[i].item1){
                item1_count = item_count[j].count;
            }
            else if(item_count[j].item == frequent_pairs[i].item2){
                item2_count = item_count[j].count;
            }
        }
        frequent_pairs[i].confidence1to2 = (double) frequent_pairs[i].count / item1_count;
        frequent_pairs[i].confidence2to1 = (double) frequent_pairs[i].count / item2_count;
    }

    /********************************************************************************
    ** ITEM TRIPLES
    ********************************************************************************/
    //identifying triples of frequent items and their count
    vector<itemTriple> item_triples = getTriples(frequent_items, frequent_pairs);

    //filter to triples that are frequent
    vector<itemTriple> frequent_triples;
    for(int i = 0; i < item_triples.size(); i++){
        if(item_triples[i].count >= support){
            frequent_triples.push_back(item_triples[i]);
        }
    }

    
    //compute confidence scores
    for(int i = 0; i < frequent_triples.size(); i++){
        int pair12_count=2147483647, pair13_count=2147483647, pair23_count=2147483647;

        for(int j = 0; j < item_pairs.size(); j++){
            if((item_pairs[j].item1 == frequent_triples[i].item1 && item_pairs[j].item2 == frequent_triples[i].item2) || (item_pairs[j].item2 == frequent_triples[i].item1 && item_pairs[j].item1 == frequent_triples[i].item2)){
                pair12_count = item_pairs[j].count;
            }
            else if((item_pairs[j].item1 == frequent_triples[i].item1 && item_pairs[j].item2 == frequent_triples[i].item3) || (item_pairs[j].item2 == frequent_triples[i].item1 && item_pairs[j].item1 == frequent_triples[i].item3)){
                pair13_count = item_pairs[j].count;
            }
            else if((item_pairs[j].item1 == frequent_triples[i].item2 && item_pairs[j].item2 == frequent_triples[i].item3) || (item_pairs[j].item2 == frequent_triples[i].item2 && item_pairs[j].item1 == frequent_triples[i].item3)){
                pair23_count = item_pairs[j].count;
            }
        }
        frequent_triples[i].confidence12to3 = frequent_triples[i].count / pair12_count;
        frequent_triples[i].confidence13to2 = frequent_triples[i].count / pair13_count;
        frequent_triples[i].confidence23to1 = frequent_triples[i].count / pair23_count;
    }
    

    /********************************************************************************
    ** PRINTING TO OUTPUT
    ********************************************************************************/
    //opening output file
    ofstream outfile;
    outfile.open("output.txt");

    //sort
    sort(frequent_pairs.begin(), frequent_pairs.end(), compareConfidencePair);
    sort(frequent_triples.begin(), frequent_triples.end(), compareConfidenceTriple);

    outfile << "OUTPUT A" << endl;
    for(int i = 0; i < 5; i++){
        outfile << frequent_pairs[i].item1 << " " << frequent_pairs[i].item2 << " " << max(frequent_pairs[i].confidence1to2, frequent_pairs[i].confidence2to1) << endl;
    }

    
    outfile << "OUTPUT B" << endl;
    /*
    for(int i = 0; i < 5; i++){
        outfile << frequent_triples[i].item1 << " " << frequent_triples[i].item2 << " " << frequent_triples[i].item3 << " " << max(frequent_triples[i].confidence12to3, max(frequent_triples[i].confidence13to2, frequent_triples[i].confidence23to1)) << endl;
    }
    */

    //closing outfile
    outfile.close();
    
    return 0;
}