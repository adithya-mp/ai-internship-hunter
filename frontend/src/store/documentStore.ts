import { create } from 'zustand';

export interface DocumentItem {
  id: string;
  name: string;
  category: string;
  label: string;
  uploadDate: string;
  size: number;
  type: string;
  fileData?: string; // Base64 encoded file data URL
}

interface DocumentStoreState {
  documents: DocumentItem[];
  isLoading: boolean;
  error: string | null;
  loadDocuments: () => Promise<void>;
  addDocument: (file: File, category: string, label: string) => Promise<void>;
  updateDocumentLabel: (id: string, newLabel: string) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
}

const DB_NAME = 'ApplyIQ_Docs';
const STORE_NAME = 'documents';
const DB_VERSION = 1;

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = window.indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (e: any) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      }
    };
  });
}

export const useDocumentStore = create<DocumentStoreState>((set, get) => ({
  documents: [],
  isLoading: false,
  error: null,
  
  loadDocuments: async () => {
    set({ isLoading: true, error: null });
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.getAll();
      
      request.onsuccess = () => {
        set({ documents: request.result || [], isLoading: false });
      };
      request.onerror = () => {
        set({ error: 'Failed to load documents from database', isLoading: false });
      };
    } catch (err: any) {
      set({ error: err.message || 'IndexedDB not supported', isLoading: false });
    }
  },

  addDocument: async (file: File, category: string, label: string) => {
    set({ isLoading: true, error: null });
    try {
      const reader = new FileReader();
      
      const fileDataPromise = new Promise<string>((resolve, reject) => {
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
      });
      
      const base64Data = await fileDataPromise;
      
      const newDoc: DocumentItem = {
        id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(),
        name: file.name,
        category,
        label: label || file.name.split('.')[0],
        uploadDate: new Date().toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        }),
        size: file.size,
        type: file.type,
        fileData: base64Data
      };
      
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      store.put(newDoc);
      
      return new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => {
          set(state => ({
            documents: [...state.documents, newDoc],
            isLoading: false
          }));
          resolve();
        };
        transaction.onerror = () => {
          set({ error: 'Failed to save document to database', isLoading: false });
          reject(transaction.error);
        };
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to read file', isLoading: false });
      throw err;
    }
  },

  updateDocumentLabel: async (id: string, newLabel: string) => {
    const { documents } = get();
    const doc = documents.find(d => d.id === id);
    if (!doc) return;
    
    const updatedDoc = { ...doc, label: newLabel };
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      store.put(updatedDoc);
      
      return new Promise<void>((resolve) => {
        transaction.oncomplete = () => {
          set(state => ({
            documents: state.documents.map(d => d.id === id ? updatedDoc : d)
          }));
          resolve();
        };
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to update label' });
    }
  },

  deleteDocument: async (id: string) => {
    try {
      const db = await openDB();
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      store.delete(id);
      
      return new Promise<void>((resolve) => {
        transaction.oncomplete = () => {
          set(state => ({
            documents: state.documents.filter(d => d.id !== id)
          }));
          resolve();
        };
      });
    } catch (err: any) {
      set({ error: err.message || 'Failed to delete document' });
    }
  }
}));
