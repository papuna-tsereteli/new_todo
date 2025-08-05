import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Keyboard,
  Alert,
  SafeAreaView,
  ActivityIndicator,
  ScrollView,
  Modal, // <<< New import
} from 'react-native';
import { MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import axios from 'axios';
import { API_URL } from '@env';

export default function App() {
  const [task, setTask] = useState('');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [suggestions, setSuggestions] = useState([]);
  const [isSuggesting, setIsSuggesting] = useState(false);

  // --- New State for Search --- [cite: 1]
  const [searchQuery, setSearchQuery] = useState(''); // [cite: 1]
  const [searchResults, setSearchResults] = useState([]); // [cite: 1]
  const [isSearchLoading, setIsSearchLoading] = useState(false); // [cite: 1]
  const [isSearchModalVisible, setIsSearchModalVisible] = useState(false); // [cite: 1]

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/todos/`); // [cite: 1]
      const formattedTasks = response.data.map(t => ({...t, id: t.id.toString()})); // [cite: 1]
      setTasks(formattedTasks); // [cite: 1]
    } catch (error) {
      console.error("Error fetching tasks:", error); // [cite: 1]
      Alert.alert('Error', 'Could not fetch tasks from the server.'); // [cite: 1]
    } finally {
      setLoading(false); // [cite: 1]
    }
  };

  // --- New Search Handler Function --- [cite: 1]
  const handleSearch = async () => { // [cite: 1]
    if (searchQuery.trim() === '') { // [cite: 1]
      Alert.alert('No query entered', 'Please enter a search term.'); // [cite: 1]
      return; // [cite: 1]
    }
    Keyboard.dismiss(); // [cite: 1]
    setIsSearchLoading(true); // [cite: 1]
    try {
      const response = await axios.post(`${API_URL}/todos/search`, { query: searchQuery }); // [cite: 1]
      setSearchResults(response.data.results); // [cite: 1]
      setIsSearchModalVisible(true); // [cite: 1]
    } catch (error) {
      console.error("Error searching tasks:", error); // [cite: 1]
      Alert.alert('Error', 'Could not perform search.'); // [cite: 1]
    } finally {
      setIsSearchLoading(false); // [cite: 1]
    }
  }; // [cite: 1]

  const handleAddTask = async (taskText) => {
    const textToAdd = taskText || task; // [cite: 1]
    Keyboard.dismiss(); // [cite: 1]
    if (textToAdd.trim() === '') { // [cite: 1]
      Alert.alert('No task entered', 'Please enter a task to add.'); // [cite: 1]
      return; // [cite: 1]
    }
    try {
      const response = await axios.post(`${API_URL}/todos/`, { text: textToAdd, completed: false }); // [cite: 1]
      setTasks([...tasks, { ...response.data, id: response.data.id.toString() }]); // [cite: 1]
      setTask(''); // [cite: 1]
      if (!taskText) { // [cite: 1]
        setSuggestions([]); // [cite: 1]
      }
    } catch (error) {
      console.error("Error adding task:", error); // [cite: 1]
      Alert.alert('Error', 'Could not add the task.'); // [cite: 1]
    }
  };

  const getAiSuggestions = async () => {
    if (tasks.length < 2) { // [cite: 1]
      Alert.alert("Add More Tasks", "Please add at least two tasks to get AI suggestions."); // [cite: 1]
      return; // [cite: 1]
    }
    setIsSuggesting(true); // [cite: 1]
    try {
      const taskTexts = tasks.map(t => t.text); // [cite: 1]
      const response = await axios.post(`${API_URL}/todos/suggest`, { tasks: taskTexts }); // [cite: 1]
      setSuggestions(response.data.suggestions); // [cite: 1]
    } catch (error) {
      console.error("Error getting suggestions:", error); // [cite: 1]
      Alert.alert('Error', 'Could not get AI suggestions.'); // [cite: 1]
    } finally {
      setIsSuggesting(false); // [cite: 1]
    }
  };

  const toggleComplete = async (id) => {
    const taskToUpdate = tasks.find((t) => t.id === id); // [cite: 1]
    if (!taskToUpdate) return; // [cite: 1]
    try {
      await axios.put(`${API_URL}/todos/${id}`, { completed: !taskToUpdate.completed }); // [cite: 1]
      setTasks(tasks.map((t) => t.id === id ? { ...t, completed: !t.completed } : t)); // [cite: 1]
    } catch (error) {
      console.error("Error updating task:", error); // [cite: 1]
      Alert.alert('Error', 'Could not update the task status.'); // [cite: 1]
    }
  };

  const deleteTask = (id) => {
    Alert.alert('Delete Task', 'Are you sure you want to delete this task?', [ // [cite: 1]
      { text: 'Cancel', style: 'cancel' }, // [cite: 1]
      {
        text: 'Delete', // [cite: 1]
        onPress: async () => { // [cite: 1]
          try {
            await axios.delete(`${API_URL}/todos/${id}`); // [cite: 1]
            setTasks(tasks.filter((taskItem) => taskItem.id !== id)); // [cite: 1]
          } catch (error) {
            console.error("Error deleting task:", error); // [cite: 1]
            Alert.alert('Error', 'Could not delete the task.'); // [cite: 1]
          }
        },
        style: 'destructive', // [cite: 1]
      },
    ]);
  };

  const renderItem = ({ item }) => (
      <View style={styles.taskItem}>
        <TouchableOpacity style={styles.taskTextContainer} onPress={() => toggleComplete(item.id)}>
          <MaterialIcons name={item.completed ? 'check-circle' : 'radio-button-unchecked'} size={24} color={item.completed ? '#4CAF50' : '#ccc'} style={styles.taskIcon} />
          <Text style={[styles.taskText, item.completed && styles.taskTextCompleted]}>{item.text}</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => deleteTask(item.id)}>
          <MaterialIcons name="delete" size={24} color="#F44336" />
        </TouchableOpacity>
      </View>
  );

  // --- New Search Result Renderer --- [cite: 1]
  const renderSearchResultItem = ({ item }) => ( // [cite: 1]
      <View style={styles.searchResultItem}>
        <Text style={styles.searchResultText}>{item.text}</Text>
        <Text style={styles.searchResultScore}>Score: {item.score.toFixed(2)}</Text>
      </View>
  ); // [cite: 1]


  return (
      <SafeAreaView style={styles.container}>
        {/* --- New Search Modal --- */}
        <Modal
            animationType="slide"
            transparent={true}
            visible={isSearchModalVisible}
            onRequestClose={() => setIsSearchModalVisible(false)}
        >
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Search Results</Text>
              <FlatList
                  data={searchResults}
                  renderItem={renderSearchResultItem}
                  keyExtractor={(item) => item.id.toString()}
                  ListEmptyComponent={<Text style={styles.emptyListText}>No relevant tasks found.</Text>}
              />
              <TouchableOpacity style={styles.closeButton} onPress={() => setIsSearchModalVisible(false)}>
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>


        <View style={styles.header}>
          <Text style={styles.headerText}>My To-Do List</Text>
          {/* --- New Search Bar --- */}
          <View style={styles.searchContainer}>
            <TextInput
                style={styles.searchInput}
                placeholder="Semantic Search..."
                placeholderTextColor="#999"
                value={searchQuery}
                onChangeText={setSearchQuery}
                onSubmitEditing={handleSearch}
            />
            <TouchableOpacity style={styles.searchButton} onPress={handleSearch} disabled={isSearchLoading}>
              {isSearchLoading ? <ActivityIndicator color="#fff" /> : <FontAwesome5 name="search" size={16} color="white" />}
            </TouchableOpacity>
          </View>
        </View>

        {loading ? (
            <View style={styles.centered}>
              <ActivityIndicator size="large" color="#fff" />
            </View>
        ) : (
            <FlatList
                data={tasks}
                renderItem={renderItem}
                keyExtractor={(item) => item.id}
                style={styles.taskList}
                ListEmptyComponent={<Text style={styles.emptyListText}>No tasks yet. Add one below!</Text>}
            />
        )}

        {tasks.length >= 2 && ( // [cite: 1]
            <View style={styles.aiContainer}>
              <TouchableOpacity style={styles.aiButton} onPress={getAiSuggestions} disabled={isSuggesting}>
                {isSuggesting ? (
                    <ActivityIndicator color="#fff" />
                ) : (
                    <>
                      <FontAwesome5 name="magic" size={16} color="white" style={{marginRight: 10}}/>
                      <Text style={styles.aiButtonText}>AI Assist</Text>
                    </>
                )}
              </TouchableOpacity>
            </View>
        )}

        {suggestions.length > 0 && ( // [cite: 1]
            <View style={styles.suggestionsContainer}>
              <Text style={styles.suggestionsTitle}>Suggestions</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {suggestions.map((suggestion, index) => ( // [cite: 1]
                    <TouchableOpacity key={index} style={styles.suggestionChip} onPress={() => handleAddTask(suggestion)}>
                      <Text style={styles.suggestionText}>{suggestion}</Text>
                    </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
        )}

        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.inputContainer}>
          <TextInput
              style={styles.input}
              placeholder="Add a new task..."
              placeholderTextColor="#999"
              value={task}
              onChangeText={setTask}
              onSubmitEditing={() => handleAddTask()}
          />
          <TouchableOpacity style={styles.addButton} onPress={() => handleAddTask()}>
            <Text style={styles.addButtonText}>+</Text>
          </TouchableOpacity>
        </KeyboardAvoidingView>
      </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212' }, // [cite: 1]
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center' }, // [cite: 1]
  header: { paddingTop: 50, paddingBottom: 20, backgroundColor: '#1E1E1E', alignItems: 'center', borderBottomWidth: 1, borderBottomColor: '#333' }, // [cite: 1]
  headerText: { fontSize: 28, fontWeight: 'bold', color: '#fff', marginBottom: 20 }, // [cite: 1]
  taskList: { flex: 1, paddingHorizontal: 20, marginTop: 20 }, // [cite: 1]
  taskItem: { backgroundColor: '#1E1E1E', padding: 20, borderRadius: 10, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 15, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.2, shadowRadius: 4, elevation: 3 }, // [cite: 1]
  taskTextContainer: { flexDirection: 'row', alignItems: 'center', flex: 1 }, // [cite: 1]
  taskIcon: { marginRight: 15 }, // [cite: 1]
  taskText: { color: '#fff', fontSize: 16, flex: 1 }, // [cite: 1]
  taskTextCompleted: { textDecorationLine: 'line-through', color: '#888' }, // [cite: 1]
  inputContainer: { flexDirection: 'row', padding: 20, borderTopWidth: 1, borderTopColor: '#333', backgroundColor: '#1E1E1E' }, // [cite: 1]
  input: { flex: 1, backgroundColor: '#333', color: '#fff', paddingHorizontal: 15, paddingVertical: 15, borderRadius: 30, fontSize: 16, marginRight: 10 }, // [cite: 1]
  addButton: { width: 60, height: 60, backgroundColor: '#6200EE', borderRadius: 30, justifyContent: 'center', alignItems: 'center', elevation: 5 }, // [cite: 1]
  addButtonText: { color: '#fff', fontSize: 24, fontWeight: 'bold' }, // [cite: 1]
  emptyListText: { textAlign: 'center', marginTop: 50, color: '#999', fontSize: 16 }, // [cite: 1]
  aiContainer: { paddingHorizontal: 20, paddingVertical: 10, alignItems: 'center' }, // [cite: 1]
  aiButton: { flexDirection: 'row', backgroundColor: '#007BFF', paddingVertical: 12, paddingHorizontal: 25, borderRadius: 25, alignItems: 'center', justifyContent: 'center', elevation: 3 }, // [cite: 1]
  aiButtonText: { color: 'white', fontSize: 16, fontWeight: 'bold' }, // [cite: 1]
  suggestionsContainer: { padding: 20, borderTopWidth: 1, borderTopColor: '#333' }, // [cite: 1]
  suggestionsTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginBottom: 10 }, // [cite: 1]
  suggestionChip: { backgroundColor: '#333', paddingVertical: 8, paddingHorizontal: 15, borderRadius: 20, marginRight: 10 }, // [cite: 1]
  suggestionText: { color: '#fff', fontSize: 14 }, // [cite: 1]
// --- New Search Styles ---
  searchContainer: { flexDirection: 'row', paddingHorizontal: 20, width: '100%', marginTop: 10 }, // [cite: 1]
  searchInput: { flex: 1, backgroundColor: '#333', color: '#fff', paddingHorizontal: 15, paddingVertical: 10, borderRadius: 20, fontSize: 16, marginRight: 10 }, // [cite: 1]
  searchButton: { width: 45, height: 45, backgroundColor: '#6200EE', borderRadius: 22.5, justifyContent: 'center', alignItems: 'center' }, // [cite: 1]
// --- New Modal Styles ---
  modalContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0,0,0,0.7)' }, // [cite: 1]
  modalContent: { backgroundColor: '#1E1E1E', borderRadius: 15, padding: 20, width: '90%', maxHeight: '80%' }, // [cite: 1]
  modalTitle: { color: '#fff', fontSize: 22, fontWeight: 'bold', marginBottom: 20, textAlign: 'center' }, // [cite: 1]
  searchResultItem: { backgroundColor: '#333', padding: 15, borderRadius: 8, marginBottom: 10, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }, // [cite:1]
  searchResultText: { color: '#fff', fontSize: 16, flex: 1 }, // [cite: 1]
  searchResultScore: { color: '#bbb', fontSize: 14 }, // [cite: 1]
  closeButton: { backgroundColor: '#F44336', padding: 15, borderRadius: 8, marginTop: 20, alignItems: 'center' }, // [cite: 1]
  closeButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' }, // [cite: 1]
});