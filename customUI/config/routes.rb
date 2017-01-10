Rails.application.routes.draw do
  # get 'sessions/new'
  get    '/login',   to: 'sessions#new'
  post   '/login',   to: 'sessions#create'
  delete '/logout',  to: 'sessions#destroy'


  get 'rest/openhab_getitems'
  get 'rest/openhab_getItem'
  get '/main/application'
  root 'sessions#new'
  match '/rest/sendaction' => 'rest#middle_sendaction', via: :post
  match '/rest/getitems' => 'rest#openhab_getitems', via: :get
  match '/rest/getstate' => 'rest#openhab_getstate', via: :post
  match '/rest/updatestate' => 'rest#openhab_updatestate', via: :put
  match '/rest/sendcommand' => 'rest#openhab_sendcommand', via: :post
  match '/rest/addorupdateitem' => 'rest#openhab_addItem', via: :put
  match '/rest/deleteitem' => 'rest#openhab_deleteitem', via: :delete
  match '/rest/getItem' => 'rest#openhab_getItem', via: :get
  match '/rest/addItemToGroup' => 'rest#openhab_addItemToGroup', via: :put
  match '/rest/removeItemFromGroup' => 'rest#openhab_removeItemFromGroup', via: :delete
  match '/rest/addTagToItem' => 'rest#openhab_addTagToItem', via: :put
  match '/rest/removeTagFromItem' => 'rest#openhab_removeTagFromItem', via: :delete


  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
end
